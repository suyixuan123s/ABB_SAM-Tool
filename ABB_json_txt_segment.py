import os
import json
from tqdm import tqdm
import argparse

def normalize_segmentation(segmentation, img_width, img_height):
    '''
    对分割信息中的每个坐标点进行归一化，按照图片的宽度和高度进行比例缩放。
    segmentation: 多边形的坐标点列表
    img_width: 图像宽度
    img_height: 图像高度
    返回值: 归一化后的分割坐标列表
    '''
    normalized_seg = []
    for i in range(0, len(segmentation), 2):  # 每两个数为一组(x, y)
        x = segmentation[i] / img_width
        y = segmentation[i + 1] / img_height
        normalized_seg.append(x)
        normalized_seg.append(y)
    return normalized_seg

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_file', default=r'E:\ABB\AI\SAM-Tool\dataset\annotations.json',
                        type=str, help="COCO格式标注文件路径")
    parser.add_argument('--save_dir', default=r'E:\ABB\AI\SAM-Tool\dataset\txt', type=str,
                        help="保存YOLO格式txt标签的目录")
    args = parser.parse_args()

    # 加载COCO格式的json文件
    with open(args.json_file, 'r') as f:
        data = json.load(f)

    # 创建保存目录，如果不存在则创建
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    # 遍历每张图片的信息
    for img in tqdm(data['images']):
        img_id = img["id"]
        img_width = img["width"]  # 获取图片宽度
        img_height = img["height"]  # 获取图片高度
        filename = img["file_name"].replace('\\', '/').split('/')[-1]  # 获取文件名
        head, _ = os.path.splitext(filename)

        # 创建与图片名对应的txt文件
        txt_file_path = os.path.join(args.save_dir, head + ".txt")
        with open(txt_file_path, 'w') as f_txt:
            # 遍历标注数据并匹配当前图片的image_id
            for ann in data['annotations']:
                if ann['image_id'] == img_id:  # 检查标注是否属于该图片
                    segmentation = ann.get("segmentation", [])
                    category = ann["category_id"]  # 直接获取类别

                    # 归一化分割信息
                    if isinstance(segmentation, list) and len(segmentation) > 0:
                        for seg in segmentation:
                            if isinstance(seg, list):
                                # 将分割信息归一化
                                normalized_seg = normalize_segmentation(seg, img_width, img_height)
                                seg_str = " ".join([f"{x:.6f}" for x in normalized_seg])
                                f_txt.write(f"{category} {seg_str}\n")
