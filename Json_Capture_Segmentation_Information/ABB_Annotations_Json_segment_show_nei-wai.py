import os
import json
import random
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

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
        largest_contour = max(segmentation, key=lambda seg: len(seg)) if segmentation else []
        return largest_contour
    return segmentation


def extract_inner_contours(segmentation):
    '''
    从分割数据中提取所有内轮廓（明确减去最大外轮廓）
    '''
    if isinstance(segmentation, list) and len(segmentation) > 1:
        # 找到最大外轮廓
        largest_contour = extract_largest_contour(segmentation)
        # 去掉最大外轮廓，保留其余内轮廓
        inner_contours = [contour for contour in segmentation if contour != largest_contour]
        return inner_contours
    return []

# def polygon_difference(exterior, interiors):
#     '''
#     计算外轮廓减去内轮廓的区域
#     '''
#     exterior_path = Path(np.array(exterior))
#     patches_list = []
#
#     for interior in interiors:
#         if len(interior) >= 6 and len(interior) % 2 == 0:
#             interior_points = [(interior[i], interior[i + 1]) for i in range(0, len(interior), 2)]
#             interior_path = Path(np.array(interior_points))
#
#             # 修改：仅处理完全包含的内轮廓
#             if exterior_path.contains_path(interior_path) and not exterior_path.intersects_path(interior_path):
#                 polygon = patches.Polygon(interior_points, linewidth=0.5, edgecolor='black', facecolor='none')
#                 patches_list.append(polygon)
#
#     return patches_list


def polygon_difference(exterior, interiors):
    '''
    计算外轮廓减去内轮廓的区域
    使用 matplotlib.path.Path 进行布尔运算
    '''

    # 将外轮廓和内轮廓都转换为Path
    exterior_path = Path(np.array(exterior))

    patches_list = []

    # 将内轮廓逐一减去
    for interior in interiors:
        if len(interior) >= 6 and len(interior) % 2 == 0:
            interior_points = [(interior[i], interior[i + 1]) for i in range(0, len(interior), 2)]
            interior_path = Path(np.array(interior_points))

            # 判断外轮廓是否与内轮廓相交
            if exterior_path.contains_path(interior_path):
            # if exterior_path.contains_path(interior_path) and not exterior_path.intersects_path(interior_path):

                # 从外轮廓中减去内轮廓
                polygon = patches.Polygon(interior_points, linewidth=4, edgecolor='red', facecolor='none')
                patches_list.append(polygon)

    return patches_list


def display_image_with_annotations(image_path, annotations, img_width, img_height, output_dir):
    '''
    显示图片，并在图片上绘制外轮廓减去内轮廓的信息，同时保存带标注的图片到指定文件夹
    '''
    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    dpi = 100  # 设置 DPI（可根据需要调整）
    figsize = (img_width / dpi, img_height / dpi)  # 将像素转换为英寸
    fig, ax = plt.subplots(1, figsize=figsize, dpi=dpi)
    ax.imshow(img)

    # 绘制每个标注对象的分割信息
    for ann in annotations:
        # segmentation 给出的应为像素信息，因此可以直接使用
        segmentation = ann['segmentation']

        # 提取最大外轮廓和所有内轮廓
        largest_contour = extract_largest_contour(segmentation)
        inner_contours = extract_inner_contours(segmentation)

        # 确保最大外轮廓的长度为偶数（成对的 x, y 坐标）
        if len(largest_contour) < 6 or len(largest_contour) % 2 != 0:
            print(f"跳过无效分割数据: {segmentation}")
            continue

        # 将最大外轮廓转换为多边形点
        polygon_points = [(largest_contour[i], largest_contour[i + 1]) for i in range(0, len(largest_contour), 2)]

        # 获取当前物体类别的颜色
        class_id = ann['category_id']
        color = category_colors.get(class_id, (0, 0, 0))  # 如果未定义颜色，默认为黑色

        # 绘制最大外轮廓
        polygon = patches.Polygon(polygon_points, linewidth=4, edgecolor=color, facecolor='none')
        ax.add_patch(polygon)

        # 计算外轮廓减去内轮廓，并绘制
        inner_patches = polygon_difference(polygon_points, inner_contours)
        for inner_patch in inner_patches:
            ax.add_patch(inner_patch)

        # 在图上显示类别名称
        category_name = class_mapping.get(class_id, 'Unknown')
        first_point = polygon_points[0]
        ax.text(first_point[0], first_point[1] - 10, category_name, color=color, fontsize=16, weight='bold')

    # 去掉坐标轴
    ax.axis('off')

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(image_path))

    # 保存图片
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    print(f"已保存标注图片: {output_path}")

    # 关闭图形
    plt.close(fig)


def process_annotations(json_file, image_dir, output_dir):
    '''
    批量处理注释文件并保存带标注的图片到指定文件夹
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

        print(f"处理图片: {img_info['file_name']}")

        # 显示图片并保存标注结果
        display_image_with_annotations(img_path, img_annotations, img_info['width'], img_info['height'], output_dir)


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\annotations.json'  # JSON文件路径
    image_dir = r'../dataset/images'  # 图片文件夹路径
    output_dir = r'../dataset/annotated_nei_wai_images2'  # 带标注图片的保存路径

    # 处理并保存注释文件中的标注图片
    process_annotations(json_file, image_dir, output_dir)
