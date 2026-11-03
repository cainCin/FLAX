from .fileio import convert_cassia_to_athena, load_athena_json, load_json, export_default
from .group_utils import group_by_line
from .merge_utils import merge_group_textlines
from .location_utils import iou, get_athena_bbox
from typing import List, Dict
import hashlib
import os


def debug_text(list_textlines: List[Dict]):
    if isinstance(list_textlines, Dict):
        print(list_textlines['text'])
    elif isinstance(list_textlines, List):
        for item in list_textlines:
            debug_text(item)
        print("="*20)

class Athena:
    
    _default_format = {
        "filename": None,
        "schema_version": "2.0",
        "checksum": None,
        "file_attributes": {
            "image_quality": [],
            "need_refinement": [],
            "content_types": [],
            "region_tags": []
        },
        "file_notes": "",
        "regions": []
    }

    def __init__(self):
        pass


    
    def __call__(self, input, io_type=dict(input="athena", output="athena"), output=None):
        # read input
        data = self._load(input, io_type)

        # export output
        self._export(data, io_type, output)

    def _load(self, input, io_type):
        if io_type["input"] == "athena":
            data = load_athena_json(input)
        else:
            data = load_json(input)
        return data

    def _export(self, cassia_json, io_type, output=None):
        if io_type["output"] == "athena":
            return convert_cassia_to_athena(cassia_json, output)
        else:
            return export_default(cassia_json, output)
    

    def update_to_label(self, athena_json, cassia_input, outdir=".", filepath=None):
        infos = convert_cassia_to_athena(cassia_input)
        try:
            label = load_json(athena_json)
        except:
            label = self._default_format
            label["filename"] = athena_json.replace("label", "input").replace(".json", ".jpg") if filepath is None else os.path.basename(filepath)
            label["checksum"] = hashlib.sha256(open(filepath, "rb").read()).hexdigest()

        label["regions"] = infos["regions"]

        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, os.path.basename(athena_json))

        return export_default(label, outpath)

    def merge_textline(self, athena_json, outdir="."):
        full_label = load_json(athena_json)

        # process merge textline
        label = load_athena_json(athena_json, addition_attr=['id'])
        list_ids = [item['id'] for item in label]
        groups = group_by_line(label, distance_threshold=0.8, by_formalkey=True)
        merged_label = merge_group_textlines(groups)

        # convert back to athena
        merged_athena_label = convert_cassia_to_athena(merged_label)

        if len(label) != len(merged_label):
            to_remove = [item for item in label if item not in merged_label]
            print("TO REMOVE")
            debug_text(to_remove)

            to_merge = [item for item in merged_label if item not in label]
            print("TO MERGE")
            debug_text(to_merge)
        
        # filter out old label
        out_label = [
            item for item in full_label["regions"] if item["id"] not in list_ids
        ]
        full_label["regions"] = out_label + merged_athena_label["regions"]

        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, os.path.basename(athena_json))

        return export_default(full_label, outpath)


    def update_kv(
        self,
        athena_json,
        infos = [],
        map_fk = {},
        outdir = ".",
    ):
        # load label
        label = load_json(athena_json)

        # load info
        if isinstance(infos, str):
            infos = load_json(infos)

        # update kv
        for item in label["regions"]:
            if item['region_attributes']['structure_type'] in ["key", "value"]:
                continue
            x,y,w,h = get_athena_bbox(item['shape_attributes'])
            # fetch corresponding info to update
            overlap_infos = [
                _info for _info in infos
                if iou(_info["location"], [(x,y), (x+w,y), (x+w,y+h), (x,y+h)], iou_type=1) > 0.8
            ]

            if map_fk:
                overlap_infos = [
                    _info for _info in overlap_infos
                    if _info['formal_key'][0] in list(map_fk.keys())
                ]

            if len(overlap_infos) > 0:
                _info = overlap_infos[0]
                item['region_attributes'].update({
                    'formal_key': _info['formal_key'][0] if _info['formal_key'][0] not in map_fk else map_fk[_info['formal_key'][0]],
                    'structure_type': _info['key_type']
                })
            
            # print(item); import pdb; pdb.set_trace()
        

        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, os.path.basename(athena_json))

        return export_default(label, outpath)

# def update_kv_label(
#     athena_json='/mnt/lustre/data/flax/PROJECTS/mitsui_poc_msfpo1/Invoice/finetune/label/119_TKPMI_BL (BLUMAR S.A._魚油)_1_3.json', 
#     infos=[],
#     map_fk = {},
#     outdir="."
# ):
#     with open(athena_json, "r", encoding="utf-8") as f:
#         label = json.load(f)
    
#     if isinstance(infos, str):
#         infos = json.load(open(infos, "r", encoding="utf-8"))
    
#     for item in label["regions"]:
#         x,y,w,h = _get_region_bounding_box(item['shape_attributes'])
#         # fetch corresponding info to update
#         overlap_infos = [
#             _info for _info in infos
#             if iou(_info["location"], [(x,y), (x+w,y), (x+w,y+h), (x,y+h)], iou_type=1) > 0.8
#         ]
#         if map_fk:
#             overlap_infos = [
#                 _info for _info in overlap_infos
#                 if _info['formal_key'][0] in list(map_fk.keys())
#             ]

#         if len(overlap_infos) > 0:
#             _info = overlap_infos[0]
#             item['region_attributes'].update({
#                 'formal_key': _info['formal_key'][0] if _info['formal_key'][0] not in map_fk else map_fk[_info['formal_key'][0]],
#                 'structure_type': _info['key_type']
#             })
        
#             debug_info(item, message='UPDATE')

#     os.makedirs(outdir, exist_ok=True)
#     with open(os.path.join(outdir, os.path.basename(athena_json)), "w", encoding="utf-8") as f:
#         json.dump(label, f, indent=2, ensure_ascii=False)