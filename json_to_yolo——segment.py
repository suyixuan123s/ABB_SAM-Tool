import os
import json
from tqdm import tqdm
import argparse


def convert_polygon_to_yolo(size, segmentation):
    """
    将COCO分割格式的多边形转换为YOLO格式。
    size: (宽, 高)
    segmentation: COCO的分割多边形列表
    返回值: 归一化后的多边形点
    """
    width, height = size
    yolo_segmentation = []

    for polygon in segmentation:
        normalized_polygon = []
        for i in range(0, len(polygon), 2):
            x = polygon[i] / width
            y = polygon[i + 1] / height
            normalized_polygon.append((x, y))
        yolo_segmentation.append(normalized_polygon)

    return yolo_segmentation


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--json_file', default=r'E:\ABB\AI\SAM-Tool\dataset\annotations.json',
                        type=str, help="coco file path")
    parser.add_argument('--save_dir', default=r'E:\ABB\AI\SAM-Tool\dataset\yolo_seg', type=str,
                        help="where to save .txt labels with segmentation")
    arg = parser.parse_args()

    data = json.load(open(arg.json_file, 'r'))

    # 如果存放txt文件夹不存在，则创建
    if not os.path.exists(arg.save_dir):
        os.makedirs(arg.save_dir)

    id_map = {}

    # 解析目标类别，也就是 categories 字段，并将类别写入文件 classes.txt 中
    with open(os.path.join(arg.save_dir, 'classes.txt'), 'w') as f:
        for i, category in enumerate(data['categories']):
            f.write(f"{category['name']}\n")
            id_map[category['id']] = i

    for img in tqdm(data['images']):
        filename = img["file_name"].replace('\\', '/').split('/')[-1]
        img_width = img["width"]
        img_height = img["height"]
        img_id = img["id"]
        head, tail = os.path.splitext(filename)

        # txt文件名，与对应图片名只有后缀名不一样
        txt_name = head + ".txt"
        f_txt = open(os.path.join(arg.save_dir, txt_name), 'w')

        for ann in data['annotations']:
            if ann['image_id'] == img_id:
                category_id = ann["category_id"]
                segmentation = ann["segmentation"]

                # 转换 segmentation 信息
                yolo_segmentation = convert_polygon_to_yolo((img_width, img_height), segmentation)

                # 写入txt，共2个字段：类别ID，多边形坐标
                f_txt.write(f"{id_map[category_id]} ")
                for polygon in yolo_segmentation:
                    for point in polygon:
                        f_txt.write(f"{point[0]} {point[1]} ")
                f_txt.write("\n")

        f_txt.close()
