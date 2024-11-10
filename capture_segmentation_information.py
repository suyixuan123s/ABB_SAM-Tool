import json
import xml.etree.ElementTree as ET
import os

# 输入和输出路径
jsonPath = r"E:\ABB\AI\SAM-Tool\dataset\annotations.json"
vocPath = r"E:\ABB\AI\SAM-Tool\assets\voc"

# 读取 JSON 文件
with open(jsonPath, 'r') as f:
    data = json.load(f)

info = data["info"]
images = data["images"]
annotations = data["annotations"]
categories = data["categories"]

# 创建类别ID到类别名称的映射
dict_category = {cat['id']: cat['name'] for cat in categories}

# 处理每张图片
for img_data in images:
    # 创建 VOC XML 文件
    xml_file = ET.Element('annotation')
    ET.SubElement(xml_file, 'folder').text = 'VOC'
    ET.SubElement(xml_file, 'filename').text = os.path.basename(img_data["file_name"])
    source = ET.SubElement(xml_file, 'source')
    ET.SubElement(source, 'database').text = 'My Database'
    ET.SubElement(source, 'annotation').text = 'COCO'
    ET.SubElement(source, 'image').text = 'flickr'
    size = ET.SubElement(xml_file, 'size')
    ET.SubElement(size, 'width').text = str(img_data['width'])
    ET.SubElement(size, 'height').text = str(img_data['height'])
    ET.SubElement(size, 'depth').text = '3'
    ET.SubElement(xml_file, 'segmented').text = '1'

    # 查找该图像的所有标注
    for ann_data in annotations:
        if ann_data['image_id'] == img_data['id']:
            # 创建 XML 标注
            obj = ET.SubElement(xml_file, 'object')
            category_id = ann_data['category_id']
            class_name = dict_category[category_id]
            ET.SubElement(obj, 'name').text = class_name
            ET.SubElement(obj, 'pose').text = 'Unspecified'
            ET.SubElement(obj, 'truncated').text = '0'
            ET.SubElement(obj, 'difficult').text = '0'

            # 边界框信息
            bbox = ann_data['bbox']
            x_min = bbox[0]
            y_min = bbox[1]
            x_max = bbox[0] + bbox[2]
            y_max = bbox[1] + bbox[3]
            bndbox = ET.SubElement(obj, 'bndbox')
            ET.SubElement(bndbox, 'xmin').text = str(int(x_min))
            ET.SubElement(bndbox, 'ymin').text = str(int(y_min))
            ET.SubElement(bndbox, 'xmax').text = str(int(x_max))
            ET.SubElement(bndbox, 'ymax').text = str(int(y_max))

            # 分割信息（如果有）
            if 'segmentation' in ann_data and isinstance(ann_data['segmentation'], list):
                segmentations = ET.SubElement(obj, 'segmentations')
                for seg in ann_data['segmentation']:
                    segmentation = ET.SubElement(segmentations, 'segmentation')
                    ET.SubElement(segmentation, 'points').text = ','.join(map(str, seg))

    # 将 XML 文件保存到 VOC 目标文件夹中
    xml_str = ET.tostring(xml_file, encoding='unicode')
    xml_output_path = os.path.join(vocPath, os.path.basename(img_data["file_name"]).replace('.jpg', '.xml'))
    with open(xml_output_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)

print("转换完成！")
