import cv2
from PIL import Image, ImageDraw, ImageFont
from athena.fileio import load_athena_json
import numpy as np
import os

list_formal_key = []
def visualize(image_path, json_path, out_dir):
    image = cv2.imread(image_path)

    # load label
    label = load_athena_json(json_path, only=None, addition_attr=['tags'])

    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    db_img = ImageDraw.Draw(image_pil, "RGBA")

    for item in label:
        x, y, w, h = cv2.boundingRect(np.array(item.get("location")))
        tl, br = (x, y), (x + w, y + h)
        font_size = item.get("font_size") if item.get("font_size") else (br[1]-tl[1])//2
        # font_size = min(font_size, 12)
        font = ImageFont.truetype("/mnt/c/Users/Cain/Documents/github/prj_flax/flax/utility/fonts/fonts-japanese-gothic.ttf", font_size)
        if len(item["type"]) > 0:
            if (item["type"], item["key_type"]) not in list_formal_key and ('tq_checkmark' not in item.get('tags')):
                list_formal_key.append((item["type"], item["key_type"]))
            
            if 'tq_checkmark' in item.get('tags'):
                db_img.rectangle(tl + br, fill=(0, 0, 255, 64), width=1)
                db_img.text((tl[0] - 1, tl[1] - h//2), f"{item.get('type')}", fill="magenta", font=font)
            elif item.get('key_type') in ['value']:
                db_img.rectangle(tl + br, fill=(0, 255, 0, 64), width=1)
                db_img.text((tl[0] - 1, tl[1] - h//2), f"{item.get('type')}", fill="magenta", font=font)
                db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="red", font=font)
            elif item.get('key_type') in ['key']:
                db_img.rectangle(tl + br, fill=(255, 0, 0, 64), width=1)
                db_img.text((tl[0] - 1, tl[1] - h//2), f"{item.get('type')}", fill="magenta", font=font)
                db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="red", font=font)
        else:
            db_img.rectangle(tl + br, fill=(0, 255, 255, 64), width=3)
            db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="blue", font=font)
    
    image_pil.save(
        os.path.join(out_dir, os.path.basename(image_path)
    ))

    # list_formal_key = sorted(list_formal_key, key=lambda x: x[1])


def process(data_dir, out_dir="debug", label="label"):
    from glob import glob
    os.makedirs(out_dir, exist_ok=True)
    for image_path in glob(os.path.join(data_dir, "input", "*")):
        image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
        label_path = os.path.join(data_dir, label, "{}.json".format(image_name))
        visualize(image_path, label_path, out_dir)






if __name__ == "__main__":
    # process(
    #     "/mnt/c/Users/Cain/Documents/data/res-1709_res-1752_standard-fk-and-finetune-the-kv-general-weight-for-me-flax/train", 
    #     out_dir = "/mnt/c/Users/Cain/Documents/data/res-1709_res-1752_standard-fk-and-finetune-the-kv-general-weight-for-me-flax/train/visualize",
    # )

    process(
        "/mnt/c/Users/Cain/Documents/data/fmlifpo2_fukoku_paperbilling_flax_poc/reference/9. 入院事情報告書", 
        out_dir = "/mnt/c/Users/Cain/Documents/data/fmlifpo2_fukoku_paperbilling_flax_poc/reference/9. 入院事情報告書/visualize",
    )
    list_formal_key = sorted(list_formal_key, key=lambda x: x[1])
    for item in list_formal_key:
        print(item)

