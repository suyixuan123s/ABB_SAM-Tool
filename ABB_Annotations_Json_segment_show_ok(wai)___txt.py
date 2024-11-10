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


def save_yolo_format(txt_file, category_id, largest_contour, img_width, img_height):
    '''
    将轮廓信息保存为YOLO格式的txt文件
    YOLO格式为：类别ID + 归一化的多边形点坐标
    '''
    with open(txt_file, 'a') as f:
        # 归一化多边形点坐标（除以图片宽高）
        normalized_contour = []
        for i in range(0, len(largest_contour), 2):
            x_norm = largest_contour[i] / img_width
            y_norm = largest_contour[i + 1] / img_height
            normalized_contour.append(x_norm)
            normalized_contour.append(y_norm)

        # YOLO格式： 类别ID + 归一化后的轮廓点
        line = f"{category_id} " + " ".join(map(str, normalized_contour)) + "\n"
        f.write(line)


def process_annotations(json_file, image_dir, txt_output_dir):
    '''
    处理注释文件并保存为YOLO格式的txt文件
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

    # 遍历每张图片并提取最大外轮廓，保存为txt文件
    for img_id, img_annotations in annotations_by_image.items():
        img_info = images_info[img_id]
        img_file_name = os.path.basename(img_info['file_name'])
        img_path = os.path.join(image_dir, img_file_name)

        if not os.path.exists(img_path):
            print(f"图片文件 {img_file_name} 不存在，跳过...")
            continue

        print(f"处理图片: {img_file_name}")

        # 对应的txt文件路径
        txt_file = os.path.join(txt_output_dir, img_file_name.replace('.jpg', '.txt'))

        # 如果txt文件已经存在，先删除
        if os.path.exists(txt_file):
            os.remove(txt_file)

        # 获取图片的宽高
        img_width = img_info['width']
        img_height = img_info['height']

        # 处理每个物体的标注
        for ann in img_annotations:
            segmentation = ann['segmentation']
            class_id = ann['category_id']

            # 提取最大外轮廓
            largest_contour = extract_largest_contour(segmentation)

            # 确保最大外轮廓的长度为偶数（成对的 x, y 坐标）
            if len(largest_contour) < 6 or len(largest_contour) % 2 != 0:
                print(f"跳过无效分割数据: {segmentation}")
                continue

            # 保存为YOLO格式的txt文件
            save_yolo_format(txt_file, class_id, largest_contour, img_width, img_height)


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\dataset\annotations.json'  # JSON文件路径
    image_dir = r'E:\ABB\AI\SAM-Tool\dataset\images'  # 图片文件夹路径
    txt_output_dir = r'E:\ABB\AI\SAM-Tool\dataset\txt'  # 输出txt文件的文件夹路径

    # 确保txt输出目录存在
    if not os.path.exists(txt_output_dir):
        os.makedirs(txt_output_dir)

    # 处理注释并保存为YOLO格式
    process_annotations(json_file, image_dir, txt_output_dir)
