import os
import json

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


def save_contour_to_txt_yolo(contour, category_id, img_width, img_height, output_file):
    '''
    将最大外轮廓信息转换为YOLO格式并保存到txt文件中
    '''
    # 将分割点转换为相对于图片尺寸的归一化坐标
    normalized_contour = [(x / img_width, y / img_height) for x, y in zip(contour[::2], contour[1::2])]

    # 计算最小边界框
    x_min = min([pt[0] for pt in normalized_contour])
    y_min = min([pt[1] for pt in normalized_contour])
    x_max = max([pt[0] for pt in normalized_contour])
    y_max = max([pt[1] for pt in normalized_contour])

    # 计算中心点和宽高 (YOLO格式的框)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    bbox_width = x_max - x_min
    bbox_height = y_max - y_min

    # YOLO格式： 类别ID x_center y_center width height (归一化)
    yolo_format = f"{category_id} {x_center} {y_center} {bbox_width} {bbox_height}"

    # 将多边形分割点保存为： x1 y1 x2 y2 ... （归一化后的坐标）
    segmentation_str = " ".join([f"{pt[0]} {pt[1]}" for pt in normalized_contour])

    # 写入txt文件，只保存最大外轮廓的信息
    with open(output_file, 'w') as f:  # 用 'w' 方式打开，确保文件中只写入一次
        f.write(f"{yolo_format} {segmentation_str}\n")


def process_annotations(json_file, image_dir, output_dir):
    '''
    批量处理注释文件并将每张图片的最大外轮廓保存为YOLO格式的txt文件
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

    # 遍历每张图片
    for img_id, img_annotations in annotations_by_image.items():
        img_info = images_info[img_id]
        img_filename = os.path.basename(img_info['file_name'])
        img_name_without_ext = os.path.splitext(img_filename)[0]
        txt_output_file = os.path.join(output_dir, f"{img_name_without_ext}.txt")

        print(f"处理图片: {img_filename}")

        # 对每个注释对象提取最大外轮廓并保存到txt文件
        for ann in img_annotations:
            segmentation = ann['segmentation']

            # 提取最大外轮廓
            largest_contour = extract_largest_contour(segmentation)

            # 确保最大外轮廓长度为偶数（成对的 x, y 坐标）
            if len(largest_contour) < 6 or len(largest_contour) % 2 != 0:
                print(f"跳过无效分割数据: {segmentation}")
                continue

            # 获取类别ID
            class_id = ann['category_id']

            # 保存为YOLO格式的txt文件（只包含最大外轮廓）
            save_contour_to_txt_yolo(largest_contour, class_id, img_info['width'], img_info['height'], txt_output_file)


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\annotations.json'  # JSON文件路径
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件夹路径
    output_dir = r'E:\ABB\AI\SAM-Tool\dataset\labels'  # 输出txt文件夹路径

    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 处理注释并将最大外轮廓信息保存为YOLO格式的txt文件
    process_annotations(json_file, image_dir, output_dir)
