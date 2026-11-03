import json
import cv2
import uuid
import numpy as np
from glob import glob

def _get_boundingbox(box_shape_info):
    if box_shape_info["name"] == "rect":
        x, y, w, h = box_shape_info['x'], box_shape_info['y'], box_shape_info['width'], box_shape_info['height']
        cnt = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        shape = "rect"

    else:
        cnt = [(x, y) for (x, y) in zip(box_shape_info["all_points_x"], box_shape_info["all_points_y"])]
        shape = "polygon"
    return cnt, shape


def load_json(json_path):  
    # load input
    if isinstance(json_path, str):
        with open(json_path, "r", encoding="utf-8") as f:
            label_info = json.load(f)
    else:
        label_info = json_path
    
    return label_info


def load_athena_json(json_path, only=["key", "value"], key_list=None, field="formal_key", addition_attr=[]):
    out = []
    
    # load input
    label_info = load_json(json_path)

    # ensure input is regions
    label_info = label_info['regions'] if "regions" in label_info else label_info["attributes"]["_via_img_metadata"]["regions"]

    # converting
    for info in label_info:
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
                target = box_attributes_info['text'] if "text" in box_attributes_info else box_attributes_info['label']
                key_type = box_attributes_info.get("structure_type") if "structure_type" in box_attributes_info else box_attributes_info["key_type"]

                if only:
                    if key_type not in only: continue
                
                ## Layout info
                cnt, shape = _get_boundingbox(box_shape_info)

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
                        attr: box_attributes_info.get(attr) if attr != "id" else info.get("id")
                    })

                out.append(out_item)
                
                
            except:
                print(f"Error in {info}")

    return out


def export_default(data, output):
    if output is None:
        return data
    else:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output

def convert_cassia_to_athena(cassia_input, filename='', output=None, checksum=''):
    if isinstance(cassia_input, str):
        cassia_input = json.load(open(cassia_input, 'r', encoding='utf-8'))

    out = dict()
    #TODO: update filename
    out['filename'] = filename
    out['file_attributes'] = {'image_quality': "", 'content_types': [""], 'need_refinement': [""], 'region_tags': [""], "file_notes": ""}
    out['file_notes'] = ''
    out["schema_version"] = "2.0"
    out['checksum'] = checksum
    out['regions'] = []

    for item in cassia_input:
        x, y, w, h = cv2.boundingRect(np.array([
            (int(x), int(y))
            for (x,y) in item.get('location', [])
        ]))
        formal_key = item.get("formal_key", [""])[0] if "formal_key" in item else item.get("type", "")
        formal_key = formal_key if formal_key not in [None, "", "textline"] else ""

        data = {
            'id': uuid.uuid4().hex,
            'shape_attributes': {
                'name': 'rect',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
            },
            'region_attributes': {
                'text': item.get('text', ''),
                'alias_id': "",
                "parent_ids": "",
                "object_type": "textline",
                "structure_type": item.get("key_type", ""), #"",
                "formal_key": formal_key, #"",
                "note": item.get("note", ""),
                "tags": item.get("tags", []),
            }
        }

        out['regions'].append(data)

    return export_default(out, output)