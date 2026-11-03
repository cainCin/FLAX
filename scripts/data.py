import json
from math import e
import os
import hashlib
import shutil
import cv2
import uuid
import numpy as np
from glob import glob

from athena import Athena


def process_fullocr():
    data_dir = "/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/unlabel/test/Form3"
    out_dir = "/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/unlabel/test/Form3/label_fullocr"
    RESULT_PATH="/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_newcontract_poc_ai/output/Form3/results"
    for result in [0]: #os.listdir(RESULT_PATH):
        # results_dir = f"{RESULT_PATH}/{result}/results"    
        results_dir = RESULT_PATH
        app = Athena()
        io_type = dict(input="cassia", output="athena")
        idx = 0
        for image_path in glob(os.path.join(data_dir, "input", "*")):
            print(image_path)
            image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
            # get label
            label_path = os.path.join(data_dir, "label", image_name + ".json")
            # get result
            # result_path = os.path.join(results_dir, "_".join(image_name.split("_")[:-2]), "formcut.json")
            result_path = os.path.join(results_dir, image_name, "ocr.json")
            if os.path.exists(result_path) == False:
                continue
            # update_to_label(label_path, result_path, out_dir)
            try:
                app.update_to_label(label_path, result_path, out_dir, image_path)
            except Exception as e:
                print(e)
                continue
            # if idx == 10:
            #     app.merge_textline(label_path)

            #     break
            idx += 1


# map_fk = {
#     "doc_id": "doc_id",
#     "bank_name":  "bank_name",
#     "bank_type": "bank_type",
#     "bank_branch_name": "bank_branch_name",
#     "account_type": "account_type",
#     "account_number": "account_number",
#     "account_name_kana": "account_name_kana",
#     "customer_name_kana": "customer_name_kana",
#     "customer_tel": "customer_tel",
#     "amount": "amount",
#     "confirmed_amount": "confirmed_amount",
#     "amount_type": "amount_type",
#     "commission_fee": "commission_fee",
#     "commission_type": "commission_type",
#     "cmf": "cmf",
#     "remarks_flag": "remarks_flag",
#     "seal": "seal",
#     "numbering": "numbering",
#     "bank_use_column": "bank_use_column",
#     "transfer_date": "transfer_date",
#     "transfer_type": "transfer_type",
#     "future_date": "future_date",
#     "invalid": "invalid",
#     "total_transfer_amount": "total_transfer_amount",
#     "total_commission": "total_commission",
#     "other_bank": "other_bank",
#     "specific_form": "specific_form",
# }
# map_fk = dict(
# doc_id="doc_id",
# bank_name="bank_name",
# bank_type="bank_type",
# bank_branch_name="bank_branch_name",
# account_type="account_type",
# account_number="account_number",
# account_name_kana="account_name_kana",
# customer_name_kana="customer_name_kana",
# customer_tel="customer_tel",
# amount="amount",
# confirmed_amount="confirmed_amount",
# amount_type="amount_type",
# commission_fee="commission_fee",
# commission_type="commission_type",
# cmf="cmf",
# remarks_flag="remarks_flag",
# seal="seal",
# numbering="numbering",
# bank_use_column="bank_use_column",
# transfer_date="transfer_date",
# transfer_type="transfer_type",
# future_date="future_date",
# invalid="invalid",
# total_transfer_amount="total_transfer_amount",
# total_commission="total_commission",
# other_bank="other_bank",
# specific_form="specific_form",
# )

# map_fk={
#     "height": "height",
#     "body_weight": "body_weight",
#     "chest_x_ray_examination": "chest_x_ray_examination",
#     "blood_pressure_max_1st": "blood_pressure_max_1st",
#     "blood_pressure_min_1st": "blood_pressure_min_1st",
#     "blood_pressure_max_2nd": "blood_pressure_max_2nd",
#     "blood_pressure_min_2nd": "blood_pressure_min_2nd",
#     "hemoglobin": "hemoglobin",
#     "got": "got",
#     "alt": "alt",
#     "y_gtp": "y_gtp",
#     "ldl_measured": "ldl_measured",
#     "hdl_measured": "hdl_measured",
#     "neutral_fat": "neutral_fat",
#     "fasting_blood_sugar_level": "fasting_blood_sugar_level",
#     "hba1c": "hba1c",
#     "urine_protein": "urine_protein",
#     "urine_glycosuria": "urine_glycosuria",
#     "urine_occult_blood_reaction": "urine_occult_blood_reaction",
#     "cardiogram": "cardiogram",
#     "creatinine": "creatinine",
#     "uric_acid": "uric_acid",
#     "platelet_count": "platelet_count",
#     "upper_gastrointestinal_x_ray_examination": "upper_gastrointestinal_x_ray_examination",
# }
list_fk = [
    "height",
    "body_weight",
    "blood_pressure_max_1st",
    "blood_pressure_min_1st",
    "blood_pressure_max_2nd",
    "blood_pressure_min_2nd",
    "hemoglobin",
    "got",
    "alt",
    "y_gtp",
    "ldl_measured",
    "hdl_measured",
    "neutral_fat",
    "fasting_blood_sugar_level",
    "hba1c",
    "urine_examination",
    "urine_protein",
    "urine_glycosuria",
    "urine_occult_blood_reaction",
    "urine_occult_blood_during_menstruation",
    "creatinine",
    "uric_acid",
    "platelet_count",
    "chest_x_ray_examination",
    "cardiogram",
    "upper_gastrointestinal_examination",
    "blood_pressure",
    "timeline_this_time",
    "timeline_previous_time",
    "timeline_before_last",
    "master_key",
    "sub_key",
    "height_thistime",
    "body_weight_thistime",
    "chest_x_ray_examination_checkmark_thistime",
    "chest_x_ray_examination_findings_thistime",
    "blood_pressure_checkmark_thistime",
    "blood_pressure_max_1st_thistime",
    "blood_pressure_min_1st_thistime",
    "blood_pressure_max_2nd_thistime",
    "blood_pressure_min_2nd_thistime",
    "anemia_examination_thistime",
    "hemoglobin_thistime",
    "liver_function_examination_thistime",
    "got_thistime",
    "alt_thistime",
    "y_gtp_thistime",
    "lipid_examination_thistime",
    "ldl_measured_thistime",
    "hdl_measured_thistime",
    "neutral_fat_thistime",
    "blood_sugar_examination_thistime",
    "fasting_blood_sugar_level_thistime",
    "hba1c_thistime",
    "urine_examination_thistime",
    "urine_protein_qualitative_thistime",
    "urine_glycosuria_qualitative_thistime",
    "urine_occult_blood_reaction_qualitative_thistime",
    "urine_occult_blood_during_menstruation_thistime",
    "cardiogram_checkmark_thistime",
    "cardiogram_findings_thistime",
    "creatinine_thistime",
    "uric_acid_thistime",
    "platelet_count_thistime",
    "upper_gastrointestinal_examination_checkmark_thistime",
    "upper_gastrointestinal_examination_findings_thistime",
    "chest_x_ray_examination_thistime",
    "cardiogram_thistime",
    "upper_gastrointestinal_examination_thistime",
    "height_previoustime",
    "body_weight_previoustime",
    "chest_x_ray_examination_checkmark_previoustime",
    "chest_x_ray_examination_findings_previoustime",
    "blood_pressure_checkmark_previoustime",
    "blood_pressure_max_1st_previoustime",
    "blood_pressure_min_1st_previoustime",
    "blood_pressure_max_2nd_previoustime",
    "blood_pressure_min_2nd_previoustime",
    "anemia_examination_previoustime",
    "hemoglobin_previoustime",
    "liver_function_examination_previoustime",
    "got_previoustime",
    "alt_previoustime",
    "y_gtp_previoustime",
    "lipid_examination_previoustime",
    "ldl_measured_previoustime",
    "hdl_measured_previoustime",
    "neutral_fat_previoustime",
    "blood_sugar_examination_previoustime",
    "fasting_blood_sugar_level_previoustime",
    "hba1c_previoustime",
    "urine_examination_previoustime",
    "urine_protein_qualitative_previoustime",
    "urine_glycosuria_qualitative_previoustime",
    "urine_occult_blood_reaction_qualitative_previoustime",
    "urine_occult_blood_during_menstruation_previoustime",
    "cardiogram_checkmark_previoustime",
    "cardiogram_findings_previoustime",
    "creatinine_previoustime",
    "uric_acid_previoustime",
    "platelet_count_previoustime",
    "upper_gastrointestinal_examination_checkmark_previoustime",
    "upper_gastrointestinal_examination_findings_previoustime",
    "chest_x_ray_examination_previoustime",
    "cardiogram_previoustime",
    "upper_gastrointestinal_examination_previoustime",
    "height_timebeforelast",
    "body_weight_timebeforelast",
    "chest_x_ray_examination_checkmark_timebeforelast",
    "chest_x_ray_examination_findings_timebeforelast",
    "blood_pressure_checkmark_timebeforelast",
    "blood_pressure_max_1st_timebeforelast",
    "blood_pressure_min_1st_timebeforelast",
    "blood_pressure_max_2nd_timebeforelast",
    "blood_pressure_min_2nd_timebeforelast",
    "anemia_examination_timebeforelast",
    "hemoglobin_timebeforelast",
    "liver_function_examination_timebeforelast",
    "got_timebeforelast",
    "alt_timebeforelast",
    "y_gtp_timebeforelast",
    "lipid_examination_timebeforelast",
    "ldl_measured_timebeforelast",
    "hdl_measured_timebeforelast",
    "neutral_fat_timebeforelast",
    "blood_sugar_examination_timebeforelast",
    "fasting_blood_sugar_level_timebeforelast",
    "hba1c_timebeforelast",
    "urine_examination_timebeforelast",
    "urine_protein_qualitative_timebeforelast",
    "urine_glycosuria_qualitative_timebeforelast",
    "urine_occult_blood_reaction_qualitative_timebeforelast",
    "urine_occult_blood_during_menstruation_timebeforelast",
    "cardiogram_checkmark_timebeforelast",
    "cardiogram_findings_timebeforelast",
    "creatinine_timebeforelast",
    "uric_acid_timebeforelast",
    "platelet_count_timebeforelast",
    "upper_gastrointestinal_examination_checkmark_timebeforelast",
    "upper_gastrointestinal_examination_findings_timebeforelast",
    "chest_x_ray_examination_timebeforelast",
    "cardiogram_timebeforelast",
    "upper_gastrointestinal_examination_timebeforelast",
]
map_fk = {
    k: k for k in list_fk
}

map_fk = {}

def process_kv():
    data_dir = "/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/unlabel/test/Form1/label_fullocr"
    results_dir = "/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_newcontract_poc_ai/output/Form1/results"
    out_dir = "/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/unlabel/test/Form1/label_kv"

    app = Athena()
    io_type = dict(input="cassia", output="athena")
    idx = 0
    for label_path in glob(os.path.join(data_dir, "*json")):
        print(label_path)
        image_name = ".".join(os.path.basename(label_path).split(".")[:-1])
        # get result
        result_path = os.path.join(results_dir, image_name, "kv.json")
        if os.path.exists(result_path) == False:
            continue

        # update_to_label(label_path, result_path, out_dir)
        app.update_kv(label_path, infos=result_path, outdir=out_dir, map_fk=map_fk)
        idx += 1


def process_merge(data_dir="/mnt/c/Users/Cain/Documents/data/fkfgfpd7_ffg_flax_request-form-for-transfer_formchange_production_add2_cr5/form4"):
    app = Athena()
    out_dir = "tmp"
    os.makedirs(out_dir, exist_ok=True)
    for label_path in glob(os.path.join(data_dir, "label_kv", "*")):
        print(label_path)
        app.merge_textline(label_path, out_dir)
    

def process_checkmark():
    from object_detection.yolo.model import YoloE
    from athena.location_utils import iou, get_athena_bbox
    # m = Yolo("/mnt/c/Users/Cain/Workspace/github/prj_flax_fukoku_newcontract_poc_ai/weight/object_detection/v20250117_checkmark_yolo_fukoku.pt", confidence=0.2)
    m = YoloE("/mnt/c/Users/Cain/Workspace/pretrain/yoloe_newcontract_2025Q3.pt", confidence=0.01)
    # data_dir = "/mnt/c/Users/Cain/Documents/data/fmlifpo2_fukoku_paperbilling_flax_poc/auto"
    # label_dir = "/mnt/c/Users/Cain/Documents/data/fmlifpo2_fukoku_paperbilling_flax_poc/auto/label_fullocr"
    # out_dir = "/mnt/c/Users/Cain/Documents/data/fmlifpo2_fukoku_paperbilling_flax_poc/auto/label_w_checkmark"

    data_dirs = [
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Asahi",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/FSH",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Res-1955",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/SBI",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/train",
        "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/test",
    ]
    label_dirs = [
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Asahi/label",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/FSH/label",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Res-1955/label",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/SBI/label",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/train/label",
        "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/test/label",
    ]
    out_dirs = [
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Asahi/label_w_checkmark",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/FSH/label_w_checkmark",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/Res-1955/label_w_checkmark",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/SBI/label_w_checkmark",
        # "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/train/label_w_checkmark",
        "/mnt/c/Users/Cain/Workspace/data/res-2028_annotation_for_checkmark_data/test/label_w_checkmark",
    ]

    for data_dir, label_dir, out_dir in zip(data_dirs, label_dirs, out_dirs):
        os.makedirs(out_dir, exist_ok=True)

        for image_path in glob(os.path.join(data_dir, "input", "*")):
            print(image_path)
            image_name = ".".join(os.path.basename(image_path).split(".")[:-1])
            # get label
            # label_path = os.path.join(label_dir, image_name + ".json")
            # get result
            checkmark_result = m.process(image_path, to_label=True)

            # update_to_label(label_path, result_path, out_dir)
            # with open(label_path, "r") as f:
            #     label = json.load(f)

            label = dict(regions=[])

            #TODO: verify if checkmark is labeled
            checkmark_labels = [
                item for item in label["regions"] 
                if "tq_checkmark" in item["region_attributes"]["tags"]
            ]
            
            error_boxes = []
            match_labeled = []
            for cm in checkmark_labels:
                predicted_boxes = [
                    item for item in checkmark_result
                    if iou(
                        get_athena_bbox(cm["shape_attributes"]),
                        get_athena_bbox(item["shape_attributes"]),
                        iou_type=1
                    ) > 0.5
                ]

                if len(predicted_boxes) == 0:
                    error_boxes.append(cm)
                else:
                    match_labeled.extend(predicted_boxes)

            if True: #len(error_boxes) > 2 or len(checkmark_labels) == 0:
                #TODO: visualize checkmark result
                image = cv2.imread(image_path)
                for cm in checkmark_result:
                    x,y,w,h = cm["shape_attributes"]["x"], cm["shape_attributes"]["y"], cm["shape_attributes"]["width"], cm["shape_attributes"]["height"]
                    if 'status=checked' in cm["region_attributes"]["note"]:
                        cv2.rectangle(image, (x,y), (x+w,y+h), (255,0,0), 2 )   # blue
                    elif 'dash' in cm["region_attributes"]["note"]:
                        cv2.rectangle(image, (x,y), (x+w,y+h), (0,0, 255), 2 )   # red
                    else:
                        cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

                for cm in error_boxes:
                    x,y,w,h = cm["shape_attributes"]["x"], cm["shape_attributes"]["y"], cm["shape_attributes"]["width"], cm["shape_attributes"]["height"]
                    cv2.rectangle(image, (x,y), (x+w,y+h), (255,255,0), -1) # cyan

                cv2.imwrite(os.path.join(out_dir, image_name + ".jpg"), image)


            #TODO: update tags for checkmark
            for item in checkmark_result:
                # update tags for checkmark
                if not item["region_attributes"].get("tags", []):
                    item["region_attributes"]["tags"] = ["tq_checkmark"]
                elif "tq_checkmark" not in item["region_attributes"]["tags"]:
                    item["region_attributes"]["tags"].append("tq_checkmark")

            label["regions"].extend([
                item for item in checkmark_result
                if item not in match_labeled
            ])

            with open(os.path.join(out_dir, image_name + ".json"), "w") as f:
                json.dump(label, f, indent=2, ensure_ascii=False)


def process_ocr(data_dir="/mnt/c/Users/Cain/Documents/data/ocr/HW/asahimutuallifeinsurance-sales-survey_poc_amlifpo2/test"):
    from ocr.autoregressive.model import AutoregressiveOCR
    WEIGHT_PATH = os.environ.get("WEIGHT_PATH", "/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_newcontract_poc_ai/weight/ocr/v20250220_ocr_autoregressive_finetune_fukoku.pt")
    m = AutoregressiveOCR(WEIGHT_PATH)
    # data_dir = "/mnt/c/Users/Cain/Documents/data/ocr/HW/asahimutuallifeinsurance-sales-survey_poc_amlifpo2/test"
    out_dir = f"{data_dir}/label_ocr"
    os.makedirs(out_dir, exist_ok=True)
    def get_snippet(image, item):
        if item["shape_attributes"]["name"] == "rect":
            x = item["shape_attributes"]["x"]
            y = item["shape_attributes"]["y"]
            w = item["shape_attributes"]["width"]
            h = item["shape_attributes"]["height"]
        else:
            x,y,w,h = cv2.boundingRect(np.array(list(zip(item["shape_attributes"]["all_points_x"],item["shape_attributes"]["all_points_y"]))))
        
        return image[max(y,0):y+h, max(x,0):x+w]
    
    def get_bbox(image, item):
        if item["shape_attributes"]["name"] == "rect":
            x = item["shape_attributes"]["x"]
            y = item["shape_attributes"]["y"]
            w = item["shape_attributes"]["width"]
            h = item["shape_attributes"]["height"]
        else:
            x,y,w,h = cv2.boundingRect(np.array(
                list(zip(item["shape_attributes"]["all_points_x"],item["shape_attributes"]["all_points_y"]))
            ))
        
        return x,y,w,h

    for image_path in glob(os.path.join(data_dir, "input", "*")):
        print(image_path)
        image = cv2.imread(image_path)
        image_name = ".".join(os.path.basename(image_path).split(".")[:-1])

        if os.path.exists(os.path.join(out_dir, image_name + ".json")):
            continue
        
        # get label
        label_path = os.path.join(data_dir, "label", image_name + ".json")
        
        # get label
        label = json.load(open(label_path, "r"))

        # filter out wrong label
        label["regions"] = [
            item for item in label["regions"]
            if get_bbox(image, item)[2] > 2 and get_bbox(image, item)[3] > 2
        ]
        
        # update ocr
        ocr_input = [
            get_snippet(image, item)
            for item in label["regions"]
        ]

        try:
            ocr_result = m.process(ocr_input)

        except Exception as e:
            print(e)
            import pdb; pdb.set_trace()

        for item, result in zip(
            label["regions"],
            ocr_result
        ):
            # skip formal key
            if item["region_attributes"]["structure_type"] in ["key", "value"] and len(item["region_attributes"]["formal_key"]) > 0:
                continue

            # proceed update ocr
            item["region_attributes"]["text"] = result["text"]
            continue

            # proceed verify ocr
            # remove "" tags
            if "" in item["region_attributes"]["tags"]:
                item["region_attributes"]["tags"].remove("")

            # update ocr to note
            item["region_attributes"]["note"] = result["text"]

            if item["region_attributes"]["structure_type"] in ["key", "value"] and len(item["region_attributes"]["formal_key"]) > 0:
                if item["region_attributes"]["text"] != result["text"]:
                    item["region_attributes"]["tags"].append("tq_hard_to_read")

        with open(os.path.join(out_dir, image_name + ".json"), "w") as f:
            json.dump(label, f, indent=2, ensure_ascii=False)



def process_rotate(data_dir="/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/form6_hc"):
    from preprocessing.rotation_deskew.jeff.model import JeffRotateDeskew
    from glob import glob
    m = JeffRotateDeskew(
        weight_path_rotation="/mnt/c/Users/Cain/Documents/github/prj_flax_fukoku_flax_paperbilling_poc_ai/weight/preprocess_general/JeffRotation_resnet18_v2_val_acc_1.00.pt",
        weight_path_deskew=None,
        enable_rotation=True,
        enable_deskew=False,
    )
    os.makedirs(os.path.join(data_dir, "output"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "low_confidence"), exist_ok=True)
    for image_path in glob(os.path.join(data_dir, "input", "*")):
        print(image_path)
        out = m.process(image_path)[0]
        output_angle = out["metadata"]["rotate_angle"]
        output_confidence = out["confidence_rotate"]

        if (output_angle % 360) != 0 and output_confidence > 0.85:
            cv2.imwrite(
                os.path.join(data_dir, "output", os.path.basename(image_path)),
                out["output"]
            )
            print(f"Rotated {os.path.basename(image_path)} by {output_angle} degrees with confidence {output_confidence}")
        elif output_confidence <= 0.85:
            # copy low confidence image to output
            cv2.imwrite(
                os.path.join(data_dir, "low_confidence", os.path.basename(image_path)),
                out["output"]
            )
            print(f"Skipped {os.path.basename(image_path)} due to low confidence: {output_confidence}")




if __name__ == "__main__":
    # process_rotate()
    # process_fullocr()
    # process_kv()
    process_checkmark()
    # process_merge()

    # process_ocr("/mnt/c/Users/Cain/Documents/data/res-1955_strengthen_current_solutions_for_hw")
    # process_ocr("/mnt/c/Users/Cain/Documents/data/ocr/HW/asahimutuallifeinsurance-sales-survey_poc_amlifpo2/test")
    # process_ocr("/mnt/c/Users/Cain/Documents/data/ocr/HW/prod_pmj2/train")
    # process_ocr("/mnt/c/Users/Cain/Documents/data/ocr/HW/prod_pmj2/validation")
    # process_ocr("/mnt/c/Users/Cain/Documents/data/fmlifd4581_fukoku_newcontract_flax_poc/run_ocr")
