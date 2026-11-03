import cv2
from athena.fileio import load_athena_json
import json
import numpy as np
from glob import glob
from athena import Athena
import os

LAYOUT_PRETRAIN = "/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_flax_paperbilling_poc_ai/weight/dc/v20241004_layout_dc_general_finetune_epoch_209_acc-89.79.pth"
OCR_PRETRAIN = "/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_flax_paperbilling_poc_ai/weight/autoregressive/v20241112_ocr_autoregressive_finetune_Q3_HW_deskew.pt"
from layout import DcLayout
from ocr import AutoregressiveOCR
mlayout = DcLayout(weights_path=LAYOUT_PRETRAIN, resize_image_shape=1536)
mocr = AutoregressiveOCR(weights_path=OCR_PRETRAIN)


def compute_overlap(bbox1, bbox2, crite=min):
    '''
        Format: (x1, y1, x2, y2)
    '''
    x1 = max(bbox1[0], bbox2[0])
    x2 = min(bbox1[2], bbox2[2])
    y1 = max(bbox1[1], bbox2[1])
    y2 = min(bbox1[3], bbox2[3])
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    if x2 < x1 or y2 < y1 or w1 * w2 * h1 * h2 == 0:
        return 0

    return (x2 - x1) * (y2 - y1) / crite(w1 * h1, w2 * h2)

def convert_pts_to_2pt(lst_points):
    '''
    Converting the 4-points format of a bounding box to 2 point format
    Convert list point [(x, y), ...] to (x1, y1, x2, y2)
    '''
    x1 = min([point[0] for point in lst_points])
    x2 = max([point[0] for point in lst_points])
    y1 = min([point[1] for point in lst_points])
    y2 = max([point[1] for point in lst_points])

    return (x1, y1, x2, y2)

def ensure_2pt(bbox):
    if all([isinstance(p, int) or isinstance(p, float) for p in bbox]):
        return bbox
    else:
        return convert_pts_to_2pt(bbox)


def remove_kv(img_cv, label=None, reverse=False):
    # load label if exist
    if isinstance(label, str):
        with open(label, "r", encoding="utf-8") as f:
            out = json.load(f)
    else:
        out = label

    # remove label
    if out is not None:
        if not reverse:
            for item in out:
                x,y,w,h = cv2.boundingRect(np.array([(int(x), (int(y)))for (x,y) in item.get('location')]))
                if item.get('key_type') in ['key', 'value']:
                    img_cv[y:y+h,x:x+w] = 255
        else:
            img = np.ones_like(img_cv, 'uint8') * 255
            for item in out:
                x,y,w,h = cv2.boundingRect(np.array([(int(x), (int(y)))for (x,y) in item.get('location')]))
                if item.get('key_type') in ['key', 'value']:
                    img[y:y+h,x:x+w] = img_cv[y:y+h,x:x+w]
            img_cv = img

    return img_cv

ls_message = []
ls_formal_key = []

def map_kv(image_path, json_path, formal_key=None):
    image = cv2.imread(image_path)
    # load label
    label = load_athena_json(json_path, key_list=formal_key)

    # filter empty kv
    label = [
        item for item in label
        if item.get('text').strip() != ""
    ]

    for idx, item in enumerate(label):
        if item.get('type'):
            if item.get('type') not in ls_formal_key:
                ls_formal_key.append(item.get('type'))
        for item2 in label[idx+1:]:
            if compute_overlap(ensure_2pt(item.get('location')), ensure_2pt(item2.get('location'))) > 0.5:
                message = f"Overlap {item.get('type')} and {item2.get('type')}"
                if message not in ls_message:
                    ls_message.append(message)
                    # print(f"Overlap {item.get('type')} and {item2.get('type')}")
    return
    #TODO: removing kv
    image_non_kv = remove_kv(image.copy(), label)

    
    #TODO: map layout ocr
    layout_output = mlayout.process(image_non_kv, unclip_ratio=2)

    flax_output = []
    for flax_item in layout_output:
        overlap_item = [
            item for item in label
            if compute_overlap(ensure_2pt(item.get('location')), ensure_2pt(flax_item.get('location'))) > 0.5
        ]
        if len(overlap_item) > 0: 
            continue
        
        # update ocr
        x1,y1, x2,y2 = ensure_2pt(flax_item.get('location'))
        try:
            ocr = mocr.process(image_non_kv[y1:y2, x1:x2], reprocess_if_more_than_n_chars=128)["text"]
        except Exception as e:
            print(f"Error {e} from position {x1,y1,x2,y2}")
            continue
        if ocr.strip() == "":
            continue
        flax_item.update({
            'text': ocr,
        })
        flax_output.append(flax_item)
    
    label.extend(flax_output)

    return label


def process(formal_key=None):
    data_dir = "/mnt/c/Users/Cain/Documents/data/res-1709_res-1752_standard-fk-and-finetune-the-kv-general-weight-for-me-flax/train"
    out_dir = "/mnt/c/Users/Cain/Documents/data/res-1709_res-1752_standard-fk-and-finetune-the-kv-general-weight-for-me-flax/train/label_mapped"
    app = Athena()
    for image_path in glob(os.path.join(data_dir, "input", "*")):
        # print(image_path)
        image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
        # get label
        label_path = os.path.join(data_dir, "label", image_name + ".json")
        
        # map kv
        label = map_kv(image_path, label_path, formal_key=formal_key)

        # update_to_label(label_path, result_path, out_dir)
        # app.update_to_label(label_path, label, out_dir)
    print("Formal Key")
    for item in ls_formal_key:
        print(item)
    print("Message")
    for item in ls_message:
        print(item)



if __name__ == "__main__":
    # ('issued_date', 'value')
    # ('page', 'key')
    # ('page_number', 'value')
    # ('name', 'key')
    # ('medical_examination_date', 'key')
    # ('patient_name;kanji', 'value')
    # ('item_text', 'key')
    # ('item_text', 'value')
    ## ('surgery_fee', 'value')
    ## ('surgery_fee;item', 'value')
    # ('billing_period', 'value')
    # ('hospital;name', 'key')
    # ('hospital;name', 'value')
    # ('type', 'key')
    # ('amount', 'key')
    # ('count', 'key')
    # ('score', 'key')
    # ('item_type', 'value')
    # ('item_score', 'value')
    ## ('surgery_name', 'value')
    ## ('surgery_fee;score', 'value')
    ## ('surgery_fee;count', 'value')
    ### ('detailed_content', 'value')
    # ('hospital;zipcode', 'value')
    # ('patient_status', 'value')
    # ('department_name', 'value')
    # ('billing_period', 'key')
    # ('patient_name;kana', 'value')
    # ('hospital;address', 'value')
    # ('medical_treatment_date', 'key')
    # ('department_name', 'key')
    ## ('billing_period;start_date', 'value')
    ## ('billing_period;end_date', 'value')
    ## ('hospitalization_fee;count', 'value')
    ## ('hospitalization_fee;item', 'value')
    ## ('hospitalization_fee;score', 'value')
    # ('document_name', 'value')
    # ('issued_date', 'key')
    # ('patient_status', 'key')
    # ('copayment_ratio', 'key')
    # ('visit_fee', 'key')
    # ('visit_fee;score', 'value')
    ## ('surgery_fee', 'key')
    # ('total_insurance_burden;score', 'key')
    # ('total_insurance_burden;score', 'value')
    # ('total_patient_copayment', 'key')
    # ('total_patient_copayment', 'value')
    # ('hospital;phone', 'value')
    # ('tel', 'key')
    # ('copayment_ratio', 'value')
    # ('birth_date', 'value')
    # ('birth_date', 'key')
    # ('kana', 'key')
    # ('medical_treatment_period', 'key')
    ## ('hospitalization_fee', 'value')
    # ('total_score', 'key')
    # ('treatment_fee', 'key')
    # ('unit_price', 'key')
    # ('from', 'key')
    # ('to', 'key')
    # ('unit_price_score', 'key')
    ## ('radiation_fee', 'key')
    # ('document_fee', 'key')
    # ('total', 'key')
    # ('copayment', 'key')
    # ('insurance', 'key')
    # ('total_insurance_burden;amount', 'value')
    # ('non_insurance', 'key')
    # ('patient_name', 'key')
    # ('transfusion_fee', 'value')
    # ('page_number', 'key')
    # ('date', 'key')
    # ('period', 'key')
    # ('address', 'key')
    ## ('hospitalization_fee', 'key')
    # ('non_insurance_treatment_fee', 'key')
    ## ('radiation_fee', 'value')
    # ('page_on_image', 'value')
    # ('issued', 'key')
    # ('medical_treatment;start_date', 'key')
    # ('medical_treatment;end_date', 'key')
    ## ('hospitalization_fee;amount', 'value')
    ## ('radiation_fee;score', 'value')
    # ('dpc_fee', 'value')
    # ('dpc_fee', 'key')
    # ('item_type', 'key')
    # ('hospital;info', 'key')
    ## ('radiation_fee;count', 'value')
    # ('item_type', '')
    # ('patient_name;kanji', 'key')
    process()
    # process([
    #     'issued_date',
    #     'page',
    #     'page_number',
    #     'name',
    #     'medical_examination_date',
    #     'patient_name;kanji',
    #     'item_text',
    #     'billing_period',
    #     'hospital;name',
    #     'type',
    #     'amount',
    #     'count',
    #     'score',
    #     'item_type',
    #     'item_score',
    #     'hospital;zipcode',
    #     'patient_status'
    #     'department_name',
    #     'patient_name;kana',
    #     'hospital;address',
    #     'medical_treatment_date',
    #     'document_name',
    #     'copayment_ratio',
    #     'visit_fee',
    #     'visit_fee;score',
    #     'total_insurance_burden;score',
    #     'total_patient_copayment',
    #     'hospital;phone',
    #     'tel',
    #     'birth_date',
    #     'kana',
    #     'medical_treatment_period',
    #     'total_score',
    #     'treatment_fee',
    #     'unit_price',
    #     'from',
    #     'to',
    #     'unit_price_score',
    #     'document_fee',
    #     'total',
    #     'copayment',
    #     'insurance',
    #     'total_insurance_burden;amount',
    #     'non_insurance',
    #     'patient_name',
    #     # 'transfusion_fee',
    #     'date',
    #     'period',
    #     'address',
    #     'non_insurance_treatment_fee',
    #     'page_on_image',
    #     'issued',
    #     'medical_treatment;start_date',
    #     'medical_treatment;end_date',
    #     'dpc_fee',
    #     'hospital;info',

    #     # 'surgery_fee;item',
    #     # 'surgery_fee;score',
    #     'surgery_fee;count',
    #     # 'surgery_fee',
    #     'radiation_fee;count',
    #     # 'radiation_fee',
    #     # 'radiation_fee;score',
    #     # 'surgery_name',
        
    #     'billing_period;start_date',
    #     'billing_period;end_date',
    #     'hospitalization_fee;count',
    #     # 'hospitalization_fee;item',
    #     # 'hospitalization_fee;score',
    #     # 'hospitalization_fee',
    #     'hospitalization_fee;amount',
    
    # ])