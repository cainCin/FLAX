

import shutil
from typing import List, Tuple
import glob
import os
import cv2
from shape import AutoShape


def visualize_gt_yolo_bbox(image_path: str, label_path: str, output_path: str) -> None:
    image = cv2.imread(image_path)
    image_height, image_width = image.shape[:2]
    with open(label_path, "r") as f:
        for line in f:
            yolo_bbox_line = line.strip()
            shape = AutoShape.from_yolo_bbox_line(yolo_bbox_line, image_width, image_height)
            if shape is not None:
                cv2.rectangle(image, (int(shape.bounding_box[0][0]), int(shape.bounding_box[0][1])), (int(shape.bounding_box[2][0]), int(shape.bounding_box[2][1])), (0, 0, 255), 2)
    cv2.imwrite(output_path, image)


def process_folder(image_dir, label_dir, output_dir) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for image_path in glob.glob(os.path.join(image_dir, "*")):
        image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
        label_path = os.path.join(label_dir, image_name + ".txt")
        output_path = os.path.join(output_dir, image_name + ".jpg")
        visualize_gt_yolo_bbox(image_path, label_path, output_path)

def extract_full_label(data_path: str, path_to_full_label: str = "/mnt/c/Users/Cain/Workspace/data/object/train/full_label.txt") -> List[Tuple[str, str]]:
    with open(path_to_full_label, "r") as f:
        list_full_label = f.readlines()

    list_full_label = [full_label.strip(".jpg") for full_label in list_full_label]
    
    output = []
    for image_path in glob.glob(os.path.join(data_path, "images", "*.jpg")):
        image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
        if image_name in list_full_label:
            continue
        
        label_path = os.path.join(data_path, "labels", image_name + ".txt")
        output.append((image_path, label_path))
    
    # move into full_label folder
    os.makedirs(os.path.join(data_path, "full_label"), exist_ok=True)
    for image_path, label_path in output:
        shutil.move(image_path, os.path.join(data_path, "full_label", "images", os.path.basename(image_path)))
        shutil.move(label_path, os.path.join(data_path, "full_label", "labels", os.path.basename(label_path)))
    return output


if __name__ == "__main__":
    # image_dir = "/mnt/c/Users/Cain/Workspace/data/object/y6_label_500/images"
    # label_dir = "/mnt/c/Users/Cain/Workspace/data/object/y6_label_500/labels"
    # output_dir = "/mnt/c/Users/Cain/Workspace/data/object/y6_label_500/visualization"
    # process_folder(image_dir, label_dir, output_dir)

    # extract_full_label(data_path="/mnt/c/Users/Cain/Workspace/data/object/train")