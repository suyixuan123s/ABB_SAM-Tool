import json
import xml.etree.ElementTree as ET
import os

jsonPath = "E:/ABB/AI/SAM-Tool/dataset/annotations.json"#改这个输入json
vocPath = "E:/ABB/AI/SAM-Tool/dataset/voc"# 改这个输出文件夹
with open(jsonPath, 'r') as f:
    data = json.load(f)

info = data["info"]
images = data["images"]
annotations = data["annotations"]
categories = data["categories"]

# 对每个图像处理
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
    ET.SubElement(xml_file, 'segmented').text = '0'

    # 查找该图像的所有标注框
    bbox_list = []
    category_ids = []
    for ann_data in annotations:
        if ann_data['image_id'] == img_data['id']:
            bbox = ann_data['bbox']
            bbox_list.append(bbox)
            category_ids.append(ann_data['category_id'])

    # 对每个标注框处理
    for i in range(len(bbox_list)):
        bbox = bbox_list[i]
        category_id = category_ids[i]
        # 转换 COCO 格式到 VOC 格式
        x_min = bbox[0]
        y_min = bbox[1]
        x_max = bbox[0] + bbox[2]
        y_max = bbox[1] + bbox[3]
        class_name = categories[category_id]['name']
        # 创建 VOC XML 标注
        obj = ET.SubElement(xml_file, 'object')
        ET.SubElement(obj, 'name').text = class_name
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = '0'
        ET.SubElement(obj, 'difficult').text = '0'
        bndbox = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(int(x_min))
        ET.SubElement(bndbox, 'ymin').text = str(int(y_min))
        ET.SubElement(bndbox, 'xmax').text = str(int(x_max))
        ET.SubElement(bndbox, 'ymax').text = str(int(y_max))

    # 将 XML 文件保存到 VOC 目标文件夹中
    xml_str = ET.tostring(xml_file)
    with open(os.path.join(vocPath, os.path.basename(img_data["file_name"]).replace('.jpg', '.xml')), 'wb') as f:
        f.write(xml_str)

