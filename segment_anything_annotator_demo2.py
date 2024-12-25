import os
import argparse
import sys

from PyQt5.QtWidgets import QApplication
from salt.editor import Editor
from salt.interface import ApplicationInterface


# 采血试管、
# 5ml_离心试管、10ml_离心试管、
# 5ml_分拣试管架(绿色）、10ml_分拣试管架（蓝色）、
# 待分拣试管架、
# 配液试管架、
# 离心机（开）、离心机（关）
# 冰箱（开）、冰箱（关）
# 分拣试管架底座、试管架存放柜


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx-model-path", type=str, default="E:/ABB/AI/SAM-Tool/sam_onnx.onnx")
    # parser.add_argument("--dataset-path", type=str, default="E:/ABB/AI/SAM-Tool/dataset")
    parser.add_argument("--dataset-path", type=str, default=r"E:\ABB\AI\Depth-Anything-V2\demo")
    parser.add_argument("--categories", type=str, default="blood_tube, "
                                                          "5ML_centrifuge_tube, 10ML_centrifuge_tube, "
                                                          "5ML_sorting_tube_rack, 10ML_sorting_tube_rack, "
                                                          "centrifuge_open, centrifuge_close, "
                                                          "refrigerator_open, refrigerator_close, "
                                                          "operating_desktop, "
                                                          "tobe_sorted_tube_rack,"
                                                          "5ML_dispensing_tube_rack, 10ML_dispensing_tube_rack"                                                                                                        
                                                          "tube_rack_storage_cabinet")
    args = parser.parse_args()

    onnx_model_path = args.onnx_model_path
    dataset_path = args.dataset_path
    categories = None
    if args.categories is not None:
        categories = args.categories.split(",")
    
    coco_json_path = os.path.join(dataset_path,"annotations.json")

    editor = Editor(
        onnx_model_path,
        dataset_path,
        categories=categories,
        coco_json_path=coco_json_path
    )

    app = QApplication(sys.argv)
    window = ApplicationInterface(app, editor)
    window.show()
    sys.exit(app.exec_())
