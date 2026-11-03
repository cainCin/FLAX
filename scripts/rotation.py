from glob import glob
import json
import os
import cv2
RESULT_PATH = '/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_flax_paperbilling_poc_ai/output/rotation'
DATA_PATH = '/mnt/c/Users/Cain/Documents/data/rotation'
# DATA_PATH = '/mnt/c/Users/Cain/Documents/TA'
OUT_PATH = "rotation_data"
LOG_PATH = "rotation_train_tmp.txt"
os.makedirs(OUT_PATH, exist_ok=True)


def read_json(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def get_page_results(result_path):
    for result in glob(f'{result_path}/*/results/*/preprocessing.json'):
        yield(result)


def extract_snippet(image, box):
    xmin, ymin, xmax, ymax = box
    return image[ymin:ymax, xmin:xmax]

def extract_image(result_path):
    image_name = result_path.split(os.sep)[-2]
    data_path = os.path.join(DATA_PATH, result_path.split(os.sep)[-4],"input","_".join(image_name.split("_")[:-2]) +".tif")

    image = cv2.imread(data_path)
    bbox = [
        read_json(result_path.replace("preprocessing.json", f"{info}.json"))
        for info in ["min_x", "min_y", "max_x", "max_y"]
    ]
    snippet = extract_snippet(image, bbox)
    print(data_path, os.path.exists(data_path))
    cv2.imwrite(os.path.join(OUT_PATH, f"{image_name}.jpg"), snippet)


def process(result_path=RESULT_PATH):
    try:
        with open(LOG_PATH, "r") as f:
            train_data = f.read().split("\n")
    except FileNotFoundError:
        train_data = []
    train_update = []
    for result in get_page_results(result_path):
        if result.split(os.sep)[-2] in train_data:
            continue
        info = read_json(result)
        try:
            info["confidence_rotate"]
        except KeyError:
            info["confidence_rotate"] = 0
        if info["confidence_rotate"] < 0.8:
            print(result)
            train_update.append(result.split(os.sep)[-2])
            extract_image(result)

    with open(LOG_PATH, "w") as f:
        f.write("\n".join(train_data + train_update))

if __name__ == '__main__':
    process()