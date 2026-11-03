from glob import glob
import json
import os
import cv2

RESULT_PATH = '/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_flax_paperbilling_poc_ai/output/rotation'
DATA_PATH = '/mnt/c/Users/Cain/Documents/data/rotation'
OUT_PATH = "skew_data"
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
    for result in get_page_results(result_path):
        info = read_json(result)
        try:
            info["metadata"]["deskew_angle"]
        except KeyError:
            info["metadata"]["deskew_angle"] = 0
        if abs(info["metadata"]["deskew_angle"]) > 3:
            print(result)
            extract_image(result)


if __name__ == '__main__':
    process()