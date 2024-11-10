# import os
# import json
# from tqdm import tqdm
# import argparse
#
#
# def convert(size, box):
#     '''
#     size: 图片的宽和高(w,h)
#     box格式: x,y,w,h
#     返回值：x_center/image_width y_center/image_height width/image_width height/image_height
#     '''
#
#     dw = 1. / (size[0])
#     dh = 1. / (size[1])
#     x = box[0] + box[2] / 2.0
#     y = box[1] + box[3] / 2.0
#     w = box[2]
#     h = box[3]
#
#     x = x * dw
#     w = w * dw
#     y = y * dh
#     h = h * dh
#     return (x, y, w, h)
#
#
# if __name__ == '__main__':
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--json_file', default=r'E:\ABB\AI\SAM-Tool\dataset\annotations.json',
#                         type=str, help="coco file path")
#     parser.add_argument('--save_dir', default=r'E:\ABB\AI\SAM-Tool\dataset\txt', type=str,
#                         help="where to save .txt labels")
#     arg = parser.parse_args()
#
#     data = json.load(open(arg.json_file, 'r'))
#
#     # 如果存放txt文件夹不存在，则创建
#     if not os.path.exists(arg.save_dir):
#         os.makedirs(arg.save_dir)
#
#     id_map = {}
#
#     # 解析目标类别，也就是 categories 字段，并将类别写入文件 classes.txt 中
#     with open(os.path.join(arg.save_dir, 'classes.txt'), 'w') as f:
#         for i, category in enumerate(data['categories']):
#             f.write(f"{category['name']}\n")
#             id_map[category['id']] = i
#
#     for img in tqdm(data['images']):
#
#         # 解析 images 字段，分别取出图片文件名、图片的宽和高、图片id
#         # filename = os.path.join(arg.image_file , img["file_name"])
#         filename = img["file_name"].replace('\\', '/').split('/')[1]
#
#         img_width = img["width"]
#         img_height = img["height"]
#         img_id = img["id"]
#         head, tail = os.path.splitext(filename)
#
#         # txt文件名，与对应图片名只有后缀名不一样
#         txt_name = head + ".txt"
#         f_txt = open(os.path.join(arg.save_dir, txt_name), 'w')
#
#         for ann in data['annotations']:
#             if ann['image_id'] == img_id:
#                 box = convert((img_width, img_height), ann["bbox"])
#
#                 # 写入txt，共5个字段
#                 f_txt.write("%s %s %s %s %s\n" % (
#                     id_map[ann["category_id"]], box[0], box[1], box[2], box[3]))
#
#         f_txt.close()
#



import os
import json
from tqdm import tqdm
import argparse

def convert(size, box):
    '''
    将COCO格式的边界框转换为YOLO格式：
    size: 图片的宽和高 (w, h)
    box: 边界框的 x_min, y_min, width, height
    返回值：x_center/image_width, y_center/image_height, width/image_width, height/image_height
    '''
    dw = 1. / size[0]
    dh = 1. / size[1]
    x_center = (box[0] + box[2] / 2.0) * dw  # x_center
    y_center = (box[1] + box[3] / 2.0) * dh  # y_center
    w = box[2] * dw  # width
    h = box[3] * dh  # height
    return (x_center, y_center, w, h)

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

    # 映射类别id到索引，并保存类别名称到 classes.txt
    id_map = {}
    with open(os.path.join(args.save_dir, 'classes.txt'), 'w') as f:
        for i, category in enumerate(data['categories']):
            f.write(f"{category['name']}\n")
            id_map[category['id']] = i

    # 遍历每张图片的信息
    for img in tqdm(data['images']):
        img_id = img["id"]
        img_width = img["width"]
        img_height = img["height"]
        filename = img["file_name"].replace('\\', '/').split('/')[-1]  # 获取文件名
        head, _ = os.path.splitext(filename)

        # 创建与图片名对应的txt文件
        txt_file_path = os.path.join(args.save_dir, head + ".txt")
        with open(txt_file_path, 'w') as f_txt:
            # 遍历标注数据并匹配当前图片的image_id
            for ann in data['annotations']:
                if ann['image_id'] == img_id:  # 检查标注是否属于该图片
                    # 提取bbox并转换为YOLO格式
                    bbox = convert((img_width, img_height), ann["bbox"])
                    class_id = id_map[ann["category_id"]]
                    # 将类别id和YOLO格式的边界框写入txt文件
                    f_txt.write(f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")

