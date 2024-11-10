import json
import os


# 定义将单个json文件转换为txt文件的函数
def convert_single_json_to_txt(json_file, output_dir):
    # 打开并读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 遍历json文件中的所有对象
    for item in data.get('shapes', []):  # 确保有'shapes'键
        category = item.get('category')  # 获取类别信息
        segmentation = item.get('segmentation')  # 获取分割信息

        # 为每个类别创建一个txt文件
        output_file = os.path.join(output_dir, f"{category}.txt")

        with open(output_file, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"Category: {category}\n")
            txt_file.write("Segmentation:\n")
            # 写入分割信息
            for segment in segmentation:
                txt_file.write(f"{segment}\n")


# 定义将整个目录的json文件批量转换为txt文件的函数
def convert_json_dir_to_txt(json_dir, output_dir):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历JSON目录中的所有文件
    for json_filename in os.listdir(json_dir):
        if json_filename.endswith(".json"):  # 确保是JSON文件
            json_file_path = os.path.join(json_dir, json_filename)
            convert_single_json_to_txt(json_file_path, output_dir)


# 使用函数，将JSON目录中的文件批量转换为TXT
json_dir = r'E:\ABB\AI\SAM-Tool\assets\json'  # 你的JSON文件目录
output_dir = r'E:\ABB\AI\SAM-Tool\assets\labels/'  # 生成的TXT文件保存路径

convert_json_dir_to_txt(json_dir, output_dir)
