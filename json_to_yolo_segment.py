import os
import json
from tqdm import tqdm


def convert_polygon(size, polygon):
    """
    将多边形的点坐标归一化到[0, 1]之间
    size: 图片的 (宽, 高)
    polygon: 多边形的点 (x1, y1, x2, y2, ...)
    返回值: 归一化后的多边形点列表
    """
    dw = 1. / size[0]
    dh = 1. / size[1]

    normalized_polygon = []
    for i in range(0, len(polygon), 2):
        x = polygon[i] * dw
        y = polygon[i + 1] * dh
        normalized_polygon.extend([x, y])

    return normalized_polygon


def export_segmentation(annotation_file, save_dir, classes):
    with open(annotation_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for img in tqdm(data['images']):
        img_width = img["width"]
        img_height = img["height"]
        img_id = img["id"]
        filename = os.path.splitext(img["file_name"])[0] + ".txt"
        txt_path = os.path.join(save_dir, filename)

        with open(txt_path, 'w') as f_txt:
            for ann in data['annotations']:
                if ann['image_id'] == img_id and 'segmentation' in ann:
                    for polygon in ann['segmentation']:
                        if isinstance(polygon, list) and len(polygon) >= 6:
                            normalized_polygon = convert_polygon((img_width, img_height), polygon)
                            normalized_polygon_str = ' '.join(map(str, normalized_polygon))
                            f_txt.write(f"{ann['category_id']} {normalized_polygon_str}\n")


# 使用方式
annotation_file = r'E:\ABB\AI\SAM-Tool\dataset\annotations.json'
save_dir = r'E:\ABB\AI\SAM-Tool\dataset\yolo_seg\labels'
classes = {
  0: "blood_tube",
  1: "5ML_centrifuge_tube",
  2: "10ML_centrifuge_tube",
  3: "5ML_sorting_tube_rack",
  4: "10ML_sorting_tube_rack",
  5: "centrifuge_open",
  6: "centrifuge_close",
  7: "refrigerator_open",
  8: "refrigerator_close",
  9: "operating_desktop",
  10: "tobe_sorted_tube_rack",
  11: "dispensing_tube_rack",
  12: "sorting_tube_rack_base",
  13: "tube_rack_storage_cabinet"
} # 你的类别名称

export_segmentation(annotation_file, save_dir, classes)
