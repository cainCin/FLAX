import json
import numpy as np
from glob import glob
DATA_PATH="/mnt/c/Users/Cain/Documents/data/gnhk/train"
import cv2
import re
from athena import Athena

def load_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


def to_polygon(item):
    if "polygon" not in item:
        return item
    
    location = item["polygon"]
    if isinstance(location, dict):
        x0, x1, x2, x3 = location["x0"], location["x1"], location["x2"], location["x3"]
        y0, y1, y2, y3 = location["y0"], location["y1"], location["y2"], location["y3"]

        polygon = [
            (x0, y0), (x1, y1), (x2, y2), (x3, y3)
        ]
    else:
        polygon = location
    return polygon


def visualize(img, data):
    for item in data:
        polygon = to_polygon(item)
        x, y, w, h = cv2.boundingRect(np.array(polygon))
        polygon = [
            (x, y), (x + w, y), (x + w, y + h), (x, y + h)
        ]
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % len(polygon)]
            img = cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
    return img


def group_by_line_id(data, skip = "%math%"):
    # sort by line_id
    data = sorted(data, key=lambda x: x["line_idx"])

    # merge text by line_id
    groups = []
    for item in data:
        if skip and re.match(skip, item["text"]):
            groups.append([])
            continue
        elif not groups:
            groups.append([item])
            continue
        
        if len(groups[-1]) == 0:
            groups[-1].append(item)
            continue
        elif item["line_idx"] == groups[-1][-1]["line_idx"]:
            groups[-1].append(item)
        else:
            groups.append([item])
    groups = [group for group in groups if group]
    return groups

def merge_group(groups):
    label = []
    for group in groups:
        item = group[0].copy()
        # update
        item["text"] = " ".join([item["text"] for item in group])
        item["polygon"] = sum([
            to_polygon(c)
            for c in group
        ], [])
        label.append(item)
    return label

def to_cassia(label):
    out = []
    for item in label:
        x,y,w,h = cv2.boundingRect(
            np.array(to_polygon(item))
        )
        out.append({
            "text": item["text"],
            "location": [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
            "key_type": "value",
            "type": "handwriting",
            "shape": "rect",
        })
    return out

def process():
    import os
    app = Athena()
    image_list = glob(DATA_PATH + "/input/*.jpg")
    tmp = "visualize"
    os.makedirs(tmp, exist_ok=True)
    for image in image_list:
        if "AF" in image:
            continue
        img = cv2.imread(image)
        json_path = image.replace(".jpg", ".json").replace("input", "label")
        label = load_json(json_path)

        # filter unreadable
        label = [item for item in label if not re.match("\%.*\%", item["text"])]
        

        # groups = group_by_line_id(label, skip="\%.*\%")
        # label = merge_group(groups)
        
        # to athena
        app.update_to_label(json_path, to_cassia(label), "gnhk")

        img = visualize(img, label)
        cv2.imwrite(os.path.join(tmp, os.path.basename(image)), img)
        

if __name__ == "__main__":
    process()