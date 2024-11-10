import os
import json
import random
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


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

# 随机生成颜色的函数
def generate_random_color():
    return (random.random(), random.random(), random.random())  # 生成RGB随机颜色

# 为每个类别生成一个随机颜色
category_colors = {category_id: generate_random_color() for category_id in class_mapping}

def load_annotations(json_file):
    '''
    解析JSON文件，获取图片和标注信息
    '''
    with open(json_file, 'r') as f:
        data = json.load(f)

    images_info = {img['id']: img for img in data['images']}
    annotations = data['annotations']

    return images_info, annotations


def extract_largest_contour(segmentation):
    '''
    从分割数据中提取最大外轮廓
    '''
    if isinstance(segmentation, list):
        # 如果是嵌套列表，选择最大长度的分割点作为最大外轮廓
        largest_contour = max(segmentation, key=lambda seg: len(seg)) if segmentation else []
        return largest_contour
    return segmentation


def display_image_with_annotations(image_path, annotations, img_width, img_height):
    '''
    显示图片，并在图片上绘制分割信息，使用直接给出的像素坐标
    '''
    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 绘制每个标注对象的分割信息
    for ann in annotations:
        # segmentation 给出的应为像素信息，因此可以直接使用
        segmentation = ann['segmentation']

        # 提取最大外轮廓
        largest_contour = extract_largest_contour(segmentation)

        # 确保 segmentation 长度为偶数（成对的 x, y 坐标）
        if len(largest_contour) < 6 or len(largest_contour) % 2 != 0:
            print(f"跳过无效分割数据: {segmentation}")
            continue

        # 将 segmentation 转换为多边形点
        polygon_points = [(largest_contour[i], largest_contour[i + 1]) for i in range(0, len(largest_contour), 2)]

        # 获取当前物体类别的颜色
        class_id = ann['category_id']
        color = category_colors.get(class_id, (0, 0, 0))  # 如果未定义颜色，默认为黑色

        # 绘制多边形，使用类别对应的颜色
        polygon = patches.Polygon(polygon_points, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(polygon)

        # 在图上显示类别名称
        category_name = class_mapping.get(class_id, 'Unknown')
        first_point = polygon_points[0]
        ax.text(first_point[0], first_point[1] - 5, category_name, color=color, fontsize=12, weight='bold')

    plt.show()


def process_annotations(json_file, image_dir):
    '''
    批量处理注释文件并可视化图片上的分割信息
    '''
    # 加载标注信息
    images_info, annotations = load_annotations(json_file)

    # 按照图片ID分组标注
    annotations_by_image = {}
    for ann in annotations:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)

    # 遍历每张图片并显示分割
    for img_id, img_annotations in annotations_by_image.items():
        img_info = images_info[img_id]
        img_path = os.path.join(image_dir, os.path.basename(img_info['file_name']))

        if not os.path.exists(img_path):
            print(f"图片文件 {img_info['file_name']} 不存在，跳过...")
            continue

        print(f"显示图片: {img_info['file_name']}")

        # 显示图片并绘制标注
        display_image_with_annotations(img_path, img_annotations, img_info['width'], img_info['height'])


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\dataset\annotations.json'  # JSON文件路径
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件夹路径

    # 处理并可视化注释文件中的图片
    process_annotations(json_file, image_dir)
