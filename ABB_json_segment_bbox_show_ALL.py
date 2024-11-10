import json
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import random


# 加载 JSON 数据
def load_json_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# 生成随机颜色
def generate_random_color():
    return (random.random(), random.random(), random.random())  # 返回RGB随机颜色


# 在图片上显示所有分割信息，并为不同物体添加不同颜色边界，同时类别名称和边界颜色一致
def display_all_segmentations(image_path, annotations, img_width, img_height, class_mapping, category_colors):
    img = Image.open(image_path)

    # 创建绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 遍历每个标注信息
    for ann in annotations:
        segmentation = ann['segmentation']  # 分割信息
        category_id = ann['category_id']  # 类别ID
        category_name = class_mapping.get(category_id, "Unknown")  # 类别名称

        # 获取对应类别的颜色
        color = category_colors.get(category_id, (1, 0, 0))  # 若无颜色，则默认为红色

        # 遍历每个物体的分割轮廓
        for seg in segmentation:
            # 提取分割点
            points = [(seg[i], seg[i + 1]) for i in range(0, len(seg), 2)]

            # 绘制分割多边形
            polygon = Polygon(points, closed=True, edgecolor=color, facecolor='none', linewidth=2)
            ax.add_patch(polygon)

            # 在分割区域上方显示类别名称，名称颜色和边界颜色一致
            ax.text(points[0][0], points[0][1] - 5, category_name, color=color, fontsize=12, weight='bold')

    plt.show()


# 处理每张图片及其所有分割信息
def process_images(json_file, image_dir):
    data = load_json_data(json_file)
    images = data['images']
    annotations = data['annotations']

    # 类别ID到类别名称的映射（根据你的数据填写）
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

    # 为每个类别生成随机颜色
    category_colors = {category_id: generate_random_color() for category_id in class_mapping}

    # 按图片ID分组标注
    annotations_by_image = {}
    for ann in annotations:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)

    # 遍历每张图片并显示分割信息
    for img_info in images:
        img_id = img_info['id']
        img_file = os.path.join(image_dir, os.path.basename(img_info['file_name']))

        if os.path.exists(img_file):
            print(f"显示图片: {img_info['file_name']}")
            display_all_segmentations(img_file, annotations_by_image.get(img_id, []), img_info['width'],
                                      img_info['height'], class_mapping, category_colors)
        else:
            print(f"图片文件 {img_info['file_name']} 不存在，跳过...")


if __name__ == '__main__':
    json_file = '/dataset/annotations.json'  # JSON 文件路径
    image_dir = '/dataset/images'  # 图片文件夹路径

    process_images(json_file, image_dir)
