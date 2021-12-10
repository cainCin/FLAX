import json
import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont


# read image
def imread(impath):
    stream = open(impath, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    img = cv2.imdecode(numpyarray, cv2.IMREAD_COLOR)
    return img

# fetch infos
def get_boundingbox(box_shape_info):
    if box_shape_info["name"] == "rect":
        x, y, w, h = box_shape_info['x'], box_shape_info['y'], box_shape_info['width'], box_shape_info['height']
        cnt = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        shape = "rect"

    else:
        cnt = [(x, y) for (x, y) in zip(box_shape_info["all_points_x"], box_shape_info["all_points_y"])]
        shape = "polygon"
    return cnt, shape

# load annotation / label from Cinnamon
_defaults_mapping = {
    "type": "formal_key",
    "text": "label",
    "key_type": "key_type",
    "location": "location",
}
def load_json(json_path, only=["key", "value"], key_list=None, field="formal_key", addition_attr=[]):
    out = []
    with open(json_path, "r", encoding="utf-8") as f:
        label_info = json.load(f)

        for info in label_info['attributes']['_via_img_metadata']['regions']:
            ## QA info
            box_shape_info = info['shape_attributes']
            box_attributes_info = info['region_attributes']

            # check condition of key
            key = box_attributes_info.get(field)
            
            if key is None: continue # key is missing
            if key_list is not None:
                get_info = key in key_list
            else:
                get_info = True
            
            ## predict if labelled
            if get_info:
                try:
                    ## Label info
                    key = box_attributes_info[field]
                    target = box_attributes_info['label']

                    key_type = box_attributes_info.get("key_type") if box_attributes_info.get("key_type") is not None \
                                    else box_attributes_info.get("type")

                    if only:
                        if key_type not in only: continue
                    
                    ## Layout info
                    cnt, shape = get_boundingbox(box_shape_info)

                    # add to ouput
                    out_item = {
                        "type": key,
                        "text": target,
                        "key_type": key_type,
                        "location": cnt,
                        "shape": shape,
                    }

                    # add additional attribution
                    for attr in addition_attr:
                        out_item.update({
                            attr: box_attributes_info.get(attr)
                        })

                    out.append(out_item)
                    
                    
                except:
                    print(f"Error in {info}")

    return out

# visualization
def visualize(img_cv, label=None, flax=None, table=None, label_text=False):
    # load image for debug
    img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    
    db_img = ImageDraw.Draw(img, "RGBA")

    # load label if exist
    if isinstance(label, str):
        with open(label, "r", encoding="utf-8") as f:
            out = json.load(f)
    else:
        out = label

    # display label
    if out is not None:
        for item in out:
            x, y, w, h = cv2.boundingRect(np.array(item.get("location")))
            tl, br = (x, y), (x + w, y + h)
            font_size = item.get("font_size") if item.get("font_size") else (br[1]-tl[1])//2
            font_size = min(font_size, 12)
            font = ImageFont.truetype("simsun.ttc", font_size)
            if item.get('key_type') in ['value']:
                db_img.rectangle(tl + br, fill=(0, 255, 0, 64), width=1)
                if label_text: 
                    db_img.text((tl[0] - 1, tl[1] - h//2), f"{item.get('type')}", fill="magenta", font=font)
                    db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="red", font=font)
            elif item.get('key_type') in ['key']:
                db_img.rectangle(tl + br, fill=(255, 0, 0, 64), width=1)
                if label_text: 
                    db_img.text((tl[0] - 1, tl[1] - h//2), f"{item.get('type')}", fill="magenta", font=font)
                    db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="red", font=font)
            else:
                db_img.rectangle(tl + br, fill=(0, 255, 255, 64), width=3)
                if label_text: 
                    db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text')}", fill="blue", font=font)

    # display flax
    if isinstance(flax, str):
        with open(flax, "r", encoding="utf-8") as f:
            flax = json.load(f)

    if flax is not None:
        for item in flax:
            x, y, w, h = cv2.boundingRect(np.array(item.get("location")))
            tl, br = (x, y), (x + w, y + h)
            font_size = item.get("font_size") if item.get("font_size") else (br[1]-tl[1])//2
            font_size = min(font_size, 12)
            font = ImageFont.truetype("simsun.ttc", font_size)
            if item.get('key_type') in ['value']:
                db_img.rectangle(tl + br, outline=(0, 0, 255, 255), width=2)
                db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text', '')}", fill="red", font=font)
            elif item.get('key_type') in ['key']:
                db_img.rectangle(tl + br, outline=(255, 0, 0, 255), width=2)
                db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text', '')}", fill="red", font=font)
            else:
                db_img.rectangle(tl + br, outline=(255, 0, 255, 128), width=1)
                db_img.text((tl[0] - 1, br[1] + 1), f"{item.get('text', '')}", fill="green", font=font)
    
    # display flax
    if isinstance(table, str):
        with open(table, "r", encoding="utf-8") as f:
            table = json.load(f)

    if table is not None:
        for item in table:
            x, y, w, h = cv2.boundingRect(np.array(item.get("location")))
            tl, br = (x, y), (x + w, y + h)
            if item.get('type') in ['cell']:
                db_img.rectangle(tl + br, outline=(0, 255, 0, 64), width=5)
            elif item.get('type') in ['table']:
                db_img.rectangle(tl + br, outline=(0, 0, 255, 255), width=5)

    return img




if __name__ == '__main__': # debug
    from matplotlib import pyplot as plt
    image_path = r"D:\Workspace\cinnamon\data\invoice\Phase 3\test\images\【TIS様】Pitch Tokyo請求書 (Aniwo)_0.jpg"
    img = imread(image_path)
    print(f"Processing {image_path}: {img.shape}")

    label_path = r"D:\Workspace\cinnamon\data\invoice\Phase 3\test\labels\【TIS様】Pitch Tokyo請求書 (Aniwo)_0.json"
    out = load_json(label_path, only=None)

    img = visualize(img, label=out)
    plt.imshow(img)
    plt.show()

