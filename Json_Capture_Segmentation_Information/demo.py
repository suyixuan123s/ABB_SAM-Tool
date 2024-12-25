"""
Author: Yixuan Su
Date: 2024/11/21 18:58
File: demo.py
Description: 
"""
import os
import json
import random
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

# 为每个类别生成一个随机颜色
def generate_random_color():
    return (random.random(), random.random(), random.random())

# 为每个类别分配颜色
category_colors = {category_id: generate_random_color() for category_id in class_mapping}

# 可视化函数
def visualize_annotations(json_file, image_dir, output_dir):
    # 加载JSON文件
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 按照图片分组标注
    images = {img['id']: img for img in data['images']}
    annotations = data['annotations']
    grouped_annotations = {}
    for annotation in annotations:
        img_id = annotation['image_id']
        if img_id not in grouped_annotations:
            grouped_annotations[img_id] = []
        grouped_annotations[img_id].append(annotation)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 遍历每张图片并绘制分割信息
    for image_id, image_info in images.items():
        img_path = os.path.join(image_dir, image_info['file_name'])
        print(f"生成的图片路径: {img_path}")

        if not os.path.exists(img_path):
            print(f"图片 {img_path} 不存在，跳过...")
            continue

        img = Image.open(img_path)
        img_width, img_height = img.size

        # 创建Matplotlib绘图
        dpi = 100
        fig, ax = plt.subplots(1, figsize=(img_width / dpi, img_height / dpi), dpi=dpi)
        ax.imshow(img)

        # 获取当前图片的标注信息
        annotations = grouped_annotations.get(image_id, [])

        for annotation in annotations:
            category_id = annotation['category_id']
            segmentation = annotation['segmentation']

            # 获取类别对应的颜色
            color = category_colors[category_id]

            # 绘制每个分割轮廓
            for seg in segmentation:
                points = [(seg[i], seg[i + 1]) for i in range(0, len(seg), 2)]
                polygon = patches.Polygon(points, linewidth=2, edgecolor=color, facecolor='none')
                ax.add_patch(polygon)

            # 显示类别名称
            category_name = class_mapping[category_id]
            if segmentation:
                first_point = (seg[0], seg[1])  # 使用分割点的第一个点
                ax.text(first_point[0], first_point[1] - 10, category_name, color=color, fontsize=12, weight='bold')

        # 去掉坐标轴
        ax.axis('off')

        # 保存图片
        output_path = os.path.join(output_dir, os.path.basename(image_info['file_name']))
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
        print(f"已保存带分割标签的图片: {output_path}")

        plt.close(fig)

# 使用函数

json_file = r'../dataset/annotations.json'  # JSON文件路径
image_dir = r'../dataset'  # 图片文件夹路径
output_dir = r'../dataset/annotated_images'  # 带标注图片的保存路径

# json_file = "path_to_annotations.json"  # 替换为实际的 JSON 文件路径
# image_dir = "path_to_images"  # 替换为实际的图片目录
# output_dir = "path_to_output_dir"  # 替换为保存输出图片的目录

visualize_annotations(json_file, image_dir, output_dir)
