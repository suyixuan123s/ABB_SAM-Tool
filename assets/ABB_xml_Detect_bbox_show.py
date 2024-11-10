import os
import xml.etree.ElementTree as ET
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def parse_voc_annotation(xml_file):
    '''
    解析单个VOC XML文件，获取图片的标注信息，包括边界框和分割信息
    '''
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 提取图片文件名和尺寸
    filename = root.find('filename').text
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)

    # 初始化一个字典来保存标注信息
    annotations = {
        'filename': filename,
        'width': width,
        'height': height,
        'objects': []
    }

    # 遍历所有的标注对象
    for obj in root.findall('object'):
        obj_name = obj.find('name').text

        # 获取边界框信息
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)

        # 获取分割信息（假设分割信息存在，格式为多边形点）
        segmentation = []
        if obj.find('segmentation') is not None:
            seg = obj.find('segmentation')
            points = seg.text.strip().split()  # 解析多边形点坐标
            segmentation = [(float(points[i]), float(points[i + 1])) for i in range(0, len(points), 2)]

        # 将对象的标注信息添加到列表中
        annotations['objects'].append({
            'name': obj_name,
            'bbox': [xmin, ymin, xmax, ymax],
            'segmentation': segmentation
        })

    return annotations


def display_annotations(annotations, image_dir):
    '''
    显示图片，并在图片上绘制边界框和分割信息
    '''
    image_path = os.path.join(image_dir, annotations['filename'])
    img = Image.open(image_path)

    # 使用 matplotlib 绘图
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 绘制每个标注对象的边界框和分割信息
    for obj in annotations['objects']:
        # 边界框信息
        bbox = obj['bbox']
        rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1],
                                 linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # 分割信息（假设有多边形的点）
        if obj['segmentation']:
            polygon = patches.Polygon(obj['segmentation'], linewidth=1, edgecolor='b', facecolor='none')
            ax.add_patch(polygon)

        # 在图上显示类别名称
        ax.text(bbox[0], bbox[1] - 5, obj['name'], color='yellow', fontsize=12, weight='bold')

    plt.show()


if __name__ == '__main__':
    voc_dir = r'E:\ABB\AI\SAM-Tool\assets\voc'  # XML文件的路径
    images_dir = r'E:\ABB\AI\SAM-Tool\assets\images'  # 图片文件的路径

    # 获取所有XML文件
    xml_files = [f for f in os.listdir(voc_dir) if f.endswith('.xml')]

    for xml_file in xml_files:
        xml_path = os.path.join(voc_dir, xml_file)
        annotations = parse_voc_annotation(xml_path)

        # 显示图片和标注信息
        display_annotations(annotations, images_dir)
