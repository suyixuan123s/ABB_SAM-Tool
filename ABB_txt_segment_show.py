import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 类别ID到类别名称的映射关系
class_mapping = {
    0: 'blood_tube',
    1: '5ML_centrifuge_tube',
    2: '10ML_centrifuge_tube',
    3: '5ML_sorting_tube_rack',
    4: '10ML_sorting_tube_rack',
    5: 'centrifuge_open',
    6: 'centrifuge_close',
    7: 'refrigerator_open',
    8: 'refrigerator_close',
    9: 'operating_desktop',
    10: 'tobe_sorted_tube_rack',
    11: 'dispensing_tube_rack',
    12: 'sorting_tube_rack_base',
    13: 'tube_rack_storage_cabinet'
}

def parse_txt_annotation(txt_file, img_width, img_height):
    '''
    解析TXT文件，获取图片的标注信息，并将归一化的分割坐标转换为实际像素坐标
    '''
    annotations_dict = {
        'filename': os.path.basename(txt_file).replace('.txt', '.jpg'),  # 假设图片文件与txt文件同名，扩展名为jpg
        'objects': []
    }

    with open(txt_file, 'r') as f:
        for line in f:
            data = line.strip().split()
            if len(data) < 2:
                continue  # 确保有类别和分割信息

            class_id = int(data[0])  # 第一项是类别ID
            category = class_mapping.get(class_id, 'unknown')  # 映射到类别名称
            segmentation = list(map(float, data[1:]))  # 后续的是归一化的分割点

            # 将归一化的分割点转换为实际像素点
            segmentation_points = [
                (segmentation[i] * img_width, segmentation[i + 1] * img_height)
                for i in range(0, len(segmentation), 2)
            ]

            annotations_dict['objects'].append({
                'name': category,
                'segmentation': segmentation_points
            })

    return annotations_dict


def display_annotations(annotations, image_dir):
    '''
    显示图片，并在图片上绘制分割信息
    '''
    image_path = os.path.join(image_dir, annotations['filename'])
    if not os.path.exists(image_path):
        print(f"图片文件 {annotations['filename']} 不存在！")
        return

    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 绘制每个标注对象的分割信息
    for obj in annotations['objects']:
        # 分割信息
        if obj['segmentation']:
            polygon = patches.Polygon(obj['segmentation'], linewidth=1, edgecolor='b', facecolor='none')
            ax.add_patch(polygon)

        # 在图上显示类别名称
        if len(obj['segmentation']) > 0:
            first_point = obj['segmentation'][0]  # 类别名称显示在分割区域的第一个点
            ax.text(first_point[0], first_point[1] - 5, obj['name'], color='yellow', fontsize=12, weight='bold')

    plt.show()


def process_txt_files_in_directory(txt_dir, images_dir):
    '''
    批量处理TXT文件，依次处理文件夹中的每个TXT文件
    '''
    # 遍历TXT文件夹中的所有TXT文件
    for txt_file in os.listdir(txt_dir):
        if txt_file.endswith('.txt'):
            txt_file_path = os.path.join(txt_dir, txt_file)
            print(f"处理文件: {txt_file_path}")

            # 找到对应的图片文件并获取其宽高
            img_file = txt_file.replace('.txt', '.jpg')
            img_path = os.path.join(images_dir, img_file)

            if not os.path.exists(img_path):
                print(f"图片文件 {img_file} 不存在，跳过...")
                continue

            # 打开图片，获取图片的宽高
            img = Image.open(img_path)
            img_width, img_height = img.size

            # 解析TXT文件，转换归一化的分割信息为实际像素坐标
            annotations = parse_txt_annotation(txt_file_path, img_width, img_height)

            # 显示图片和标注信息
            display_annotations(annotations, images_dir)


if __name__ == '__main__':
    txt_dir = r'E:\ABB\AI\SAM-Tool\dataset\txt'  # TXT文件夹路径
    images_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件的路径

    # 批量处理TXT文件
    process_txt_files_in_directory(txt_dir, images_dir)
