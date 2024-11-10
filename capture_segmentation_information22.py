import os
import xml.etree.ElementTree as ET

# 输入和输出路径
voc_folder = r"E:\ABB\AI\SAM-Tool\assets\voc"
yolo_output_folder = r"E:\ABB\AI\SAM-Tool\assets\YOLO"

# 去除输出文件夹路径中的末尾空格
yolo_output_folder = yolo_output_folder.strip()

# 创建 YOLO 输出文件夹（如果不存在）
os.makedirs(yolo_output_folder, exist_ok=True)

# 类别映射，根据您的数据集类别定义
category_mapping = {
    "centrifuge_close": 0,
    "refrigerator_close": 1,
    "sorting_tube_rack_base": 2,
    "5ML_centrifuge_tube": 3,
    "10ML_centrifuge_tube": 4,
    "blood_tube": 5,
    "5ML_sorting_tube_rack": 6,
    "10ML_sorting_tube_rack": 7,
    "tube_rack_storage_cabinet": 8
}

# 处理每个 XML 文件
for xml_file in os.listdir(voc_folder):
    if not xml_file.endswith(".xml"):
        continue

    # 解析 XML 文件
    tree = ET.parse(os.path.join(voc_folder, xml_file))
    root = tree.getroot()

    # 获取图像大小
    size = root.find("size")
    img_width = int(size.find("width").text)
    img_height = int(size.find("height").text)

    # 打开输出的 YOLO 格式 TXT 文件
    txt_filename = os.path.join(yolo_output_folder, xml_file.replace(".xml", ".txt"))
    with open(txt_filename, "w") as txt_file:
        # 遍历每个对象
        for obj in root.findall("object"):
            class_name = obj.find("name").text.strip()
            if class_name not in category_mapping:
                continue
            class_id = category_mapping[class_name]

            # 处理分割信息
            segmentations = obj.find("segmentations")
            if segmentations is not None:
                for seg in segmentations.findall("segmentation"):
                    points = seg.find("points").text.split(",")
                    normalized_points = [
                        float(points[i]) / img_width if i % 2 == 0 else float(points[i]) / img_height
                        for i in range(len(points))
                    ]
                    points_str = " ".join([f"{p:.6f}" for p in normalized_points])
                    txt_file.write(f" {class_id} {points_str}\n")

print("XML 转换为 YOLO 格式完成！")
