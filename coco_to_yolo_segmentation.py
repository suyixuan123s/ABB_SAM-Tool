import os
import json
from tqdm import tqdm


def normalize_polygon(size, polygon):
    '''
    将分割的多边形点归一化为YOLO格式：
    size: 图片的宽和高 (w, h)
    polygon: 分割的多边形点，格式为 [x1, y1, x2, y2, ..., xn, yn]
    返回值：归一化的多边形点
    '''
    dw = 1. / size[0]
    dh = 1. / size[1]
    normalized_polygon = []
    for i in range(0, len(polygon), 2):
        x = polygon[i] * dw
        y = polygon[i + 1] * dh
        normalized_polygon.append(x)
        normalized_polygon.append(y)
    return normalized_polygon


def process_annotations(json_file, save_dir):
    # 加载COCO格式的json文件
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 创建保存目录，如果不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 映射类别id到索引，并保存类别名称到 classes.txt
    id_map = {}
    with open(os.path.join(save_dir, 'classes.txt'), 'w') as f:
        for i, category in enumerate(data['categories']):
            f.write(f"{category['name']}\n")
            id_map[category['id']] = i

    # 遍历每张图片的信息
    for img in tqdm(data['images']):
        img_id = img["id"]
        img_width = img["width"]
        img_height = img["height"]
        filename = img["file_name"].replace('\\', '/').split('/')[-1]
        head, _ = os.path.splitext(filename)

        # 创建与图片名对应的txt文件
        txt_file_path = os.path.join(save_dir, head + ".txt")

        with open(txt_file_path, 'w') as f_txt:
            # 遍历标注数据并匹配当前图片的image_id
            for ann in data['annotations']:
                if ann['image_id'] == img_id:
                    category_id = ann['category_id']

                    # 提取每个 category_id 的 bbox 和 segmentation 信息
                    bbox = ann['bbox']
                    segmentation = ann['segmentation']

                    # 归一化分割数据
                    for segment in segmentation:
                        normalized_polygon = normalize_polygon((img_width, img_height), segment)
                        class_id = id_map[category_id]

                        # 将类别id和归一化后的多边形点写入txt文件
                        f_txt.write(f"{class_id} " + " ".join([f"{p:.6f}" for p in normalized_polygon]) + "\n")


if __name__ == '__main__':
    json_file = r'E:\ABB\AI\SAM-Tool\dataset\annotations.json'  # 输入的JSON文件路径
    save_dir = r'E:\ABB\AI\SAM-Tool\dataset\yolo_seg'  # 保存输出的TXT文件的目录

    process_annotations(json_file, save_dir)
