import json
import uuid
import cv2
import numpy as np


# athena_template = {
#     'filename', 
#     'checksum', 
#     'schema_version', 
#     'file_attributes', 
#     'file_notes', 
#     'regions',
# }


def convert_cassia_to_athena(cassia_input, filename='', output=None, checksum=''):
    if isinstance(cassia_input, str):
        cassia_input = json.load(open(cassia_input, 'r', encoding='utf-8'))
    
    # with open('33_1_1.json', 'r', encoding='utf-8') as f:
    #     labels = json.load(f)

    out = dict()
    #TODO: update filename
    out['filename'] = filename
    out['file_attributes'] = {'image_quality': [], 'content_types': [], 'need_refinement': [], 'region_tags': []}
    out['file_notes'] = ''
    out["schema_version"] = "2.0"
    out['checksum'] = checksum
    out['regions'] = []

    for item in cassia_input:
        x, y, w, h = cv2.boundingRect(np.array([
            (int(x), int(y))
            for (x,y) in item.get('location', [])
        ]))

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
                "structure_type": "",
                "formal_key": "",
                "note": "",
                "tags": [],
            }
        }

        out['regions'].append(data)

    if output is None:
        return out
    else:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        return

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

        for info in label_info['regions']:
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
                    target = box_attributes_info['text']
                    key_type = box_attributes_info.get("structure_type")

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


def main():
    convert_cassia_to_athena([{}])


if __name__ == '__main__':
    main()