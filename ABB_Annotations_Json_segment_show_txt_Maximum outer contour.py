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


def save_annotations_as_txt(image_path, annotations, img_width, img_height, save_dir):
    '''
    将提取的最大外轮廓信息转换为YOLO格式并保存为txt文件
    '''
    img_name = os.path.splitext(os.path.basename(image_path))[0]
    txt_file_path = os.path.join(save_dir, img_name + ".txt")

    with open(txt_file_path, 'w') as f:
        for ann in annotations:
            # segmentation 给出的应为像素信息，因此可以直接使用
            segmentation = ann['segmentation']

            # 提取最大外轮廓
            largest_contour = extract_largest_contour(segmentation)

            # 确保 segmentation 长度为偶数（成对的 x, y 坐标）
            if len(largest_contour) < 6 or len(largest_contour) % 2 != 0:
                print(f"跳过无效分割数据: {segmentation}")
                continue

            # 将 segmentation 转换为多边形点，并归一化坐标
            normalized_polygon_points = [(largest_contour[i] / img_width, largest_contour[i + 1] / img_height)
                                         for i in range(0, len(largest_contour), 2)]

            # 获取物体类别编号
            class_id = ann['category_id']

            # YOLO格式的分割文件格式： 类别编号 归一化坐标(x1, y1, x2, y2, ..., xn, yn)
            polygon_str = ' '.join([f'{x:.6f} {y:.6f}' for x, y in normalized_polygon_points])
            f.write(f"{class_id} {polygon_str}\n")


def process_annotations(json_file, image_dir, save_dir):
    '''
    批量处理注释文件，保存最大外轮廓信息为YOLO格式
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

    # 遍历每张图片并保存分割信息
    for img_id, img_annotations in annotations_by_image.items():
        img_info = images_info[img_id]
        img_path = os.path.join(image_dir, os.path.basename(img_info['file_name']))

        if not os.path.exists(img_path):
            print(f"图片文件 {img_info['file_name']} 不存在，跳过...")
            continue

        print(f"处理图片: {img_info['file_name']}")

        # 保存分割数据到txt文件
        save_annotations_as_txt(img_path, img_annotations, img_info['width'], img_info['height'], save_dir)


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\dataset\annotations.json'  # JSON文件路径
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件夹路径
    save_dir = r'E:\ABB\AI\SAM-Tool\dataset\labels'  # 保存txt文件的路径

    # 如果保存目录不存在，创建它
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 处理并保存注释文件中的分割信息到YOLO格式txt文件
    process_annotations(json_file, image_dir, save_dir)
