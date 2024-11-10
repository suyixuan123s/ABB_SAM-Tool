import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# 类别ID到类别名称的映射关系（示例）
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

# 为每个类别生成颜色
def generate_random_color():
    return (0.2 + 0.6 * os.urandom(1)[0] / 255, 0.2 + 0.6 * os.urandom(1)[0] / 255, 0.2 + 0.6 * os.urandom(1)[0] / 255)

# 每个类别的随机颜色
category_colors = {category_id: generate_random_color() for category_id in class_mapping}

def read_txt_file(txt_file, img_width, img_height):
    '''
    读取txt文件中的分割信息，并将归一化的坐标转换为像素坐标
    '''
    objects = []
    with open(txt_file, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()
            class_id = int(parts[0])
            points = [float(p) for p in parts[1:]]
            # 将归一化的坐标转换为实际的像素坐标
            polygon = [(points[i] * img_width, points[i + 1] * img_height) for i in range(0, len(points), 2)]
            objects.append({'class_id': class_id, 'polygon': polygon})
    return objects

def display_image_with_txt_annotations(image_path, txt_file, img_width, img_height):
    '''
    读取txt文件中的分割信息，并将其显示在图片上
    '''
    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 从txt文件中读取分割信息
    objects = read_txt_file(txt_file, img_width, img_height)

    # 绘制每个分割对象的多边形
    for obj in objects:
        class_id = obj['class_id']
        polygon_points = obj['polygon']
        color = category_colors.get(class_id, (0, 0, 0))  # 获取对应类别的颜色

        # 绘制多边形
        polygon = patches.Polygon(polygon_points, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(polygon)

        # 显示类别名称
        category_name = class_mapping.get(class_id, 'Unknown')
        first_point = polygon_points[0]
        ax.text(first_point[0], first_point[1] - 5, category_name, color=color, fontsize=12, weight='bold')

    plt.show()


def process_images_and_txt(image_dir, txt_dir):
    '''
    批量处理图片和对应的txt文件，显示分割信息
    '''
    for img_file in os.listdir(image_dir):
        if img_file.endswith('.jpg') or img_file.endswith('.png'):
            img_path = os.path.join(image_dir, img_file)
            img_name = os.path.splitext(img_file)[0]
            txt_file = os.path.join(txt_dir, img_name + ".txt")

            if not os.path.exists(txt_file):
                print(f"对应的txt文件 {txt_file} 不存在，跳过...")
                continue

            # 获取图片的宽高
            with Image.open(img_path) as img:
                img_width, img_height = img.size

            print(f"处理图片: {img_file}")

            # 显示图片并绘制标注
            display_image_with_txt_annotations(img_path, txt_file, img_width, img_height)


if __name__ == '__main__':
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件夹路径
    txt_dir = r'E:\ABB\AI\SAM-Tool\dataset\txt'  # 对应的txt文件路径

    # 批量处理并显示图片和txt文件中的分割信息
    process_images_and_txt(image_dir, txt_dir)
