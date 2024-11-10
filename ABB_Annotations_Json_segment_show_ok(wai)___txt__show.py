import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def load_yolo_txt(txt_file):
    '''
    加载YOLO格式的txt文件，返回每个物体的类别ID和对应的归一化轮廓点
    '''
    objects = []
    with open(txt_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            class_id = int(parts[0])
            points = list(map(float, parts[1:]))
            objects.append((class_id, points))
    return objects

def display_image_with_yolo_segments(image_path, txt_file, img_width, img_height, class_mapping, category_colors):
    '''
    显示图片，并在图片上绘制YOLO格式的分割轮廓
    '''
    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 加载txt文件中的物体信息
    objects = load_yolo_txt(txt_file)

    for class_id, points in objects:
        # 反归一化轮廓点
        polygon_points = [(points[i] * img_width, points[i + 1] * img_height) for i in range(0, len(points), 2)]

        # 获取当前物体类别的颜色
        color = category_colors.get(class_id, (0, 0, 0))  # 如果未定义颜色，默认为黑色

        # 绘制轮廓多边形
        polygon = patches.Polygon(polygon_points, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(polygon)

        # 在图上显示类别名称
        category_name = class_mapping.get(class_id, 'Unknown')
        first_point = polygon_points[0]
        ax.text(first_point[0], first_point[1] - 5, category_name, color=color, fontsize=12, weight='bold')

    plt.show()

def process_images_with_segments(image_dir, txt_output_dir, class_mapping, category_colors):
    '''
    处理每张图片并显示分割轮廓
    '''
    # 遍历每张图片
    for img_file in os.listdir(image_dir):
        if img_file.endswith('.jpg'):
            img_path = os.path.join(image_dir, img_file)
            txt_file = os.path.join(txt_output_dir, img_file.replace('.jpg', '.txt'))

            if not os.path.exists(txt_file):
                print(f"找不到txt文件 {txt_file}，跳过...")
                continue

            print(f"显示图片: {img_file}")

            # 打开图片以获取宽高
            img = Image.open(img_path)
            img_width, img_height = img.size

            # 显示图片并绘制分割轮廓
            display_image_with_yolo_segments(img_path, txt_file, img_width, img_height, class_mapping, category_colors)

if __name__ == '__main__':
    # 调用之前的功能进行分割处理（假设分割txt文件已经生成完毕）
    os.system("python ABB_Annotations_Json_segment_show_ok(wai)___txt.py")

    # 图片文件夹路径
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'
    # txt文件夹路径
    txt_output_dir = r'E:\ABB\AI\SAM-Tool\dataset\txt'

    # 类别ID到类别名称的映射关系（与之前一致）
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

    # 随机生成颜色
    import random
    def generate_random_color():
        return (random.random(), random.random(), random.random())  # 生成RGB随机颜色

    category_colors = {category_id: generate_random_color() for category_id in class_mapping}

    # 显示带有分割信息的图片
    process_images_with_segments(image_dir, txt_output_dir, class_mapping, category_colors)
