import os, json
from jsondiff import diff
from run_report import REPORT
AUTO_LABEL_PATH = "/mnt/c/Users/Cain/Documents/data/res-1527/data auto kv/batch4/label"
MANUAL_LABEL_PATH = "/mnt/c/Users/Cain/Documents/data/res-1527/batch_4/label"

TEST_JSON = "546548684058_638823569_CI_1_8.json"

def read_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)
    
def compare_label(auto_json, manual_json, compare_info=["regions"]):
    output = dict()
    for info in compare_info:
        if info not in auto_json or info not in manual_json:
            print(f"Key {info} not found in both json")
            continue
        
        # auto_info = auto_json[info]
        # manu_info = manual_json[info]
        auto_info = sorted(auto_json[info], key=lambda x: x["id"])
        manu_info = sorted(manual_json[info], key=lambda x: x["id"])

        # pop tags from compare
        for item in auto_info:
            item["region_attributes"].pop('tags', None)
        for item in manu_info:
            item["region_attributes"].pop('tags', None)

        diff_result = diff(auto_info, manu_info)
        # if diff_result:
        #     print(f"Key {info} is different: \n{diff_result}")
        #     for idx, titem in enumerate(manu_info):
        #         if idx not in diff_result:
        #             continue
        #         for item in auto_info: 
        #             if item["id"] == titem["id"]: 
        #                 print(item)
        #                 print(titem)
        #                 import pdb; pdb.set_trace()

        output[info] = diff_result
        output[f"label_{info}"] = manu_info
        output[f"effective_{info}"] = 1.0 - float(len(diff_result)) / len(manu_info)
    return output

def process_folder(auto_folder, manual_folder):
        
    os.makedirs("results", exist_ok=True)
    # process for difference
    data = []
    for json_name in os.listdir(auto_folder):
        auto_json = read_json(os.path.join(auto_folder, json_name))
        manual_json = read_json(os.path.join(manual_folder, json_name))
        difference = compare_label(auto_json, manual_json, compare_info=["regions"])

        
        # outpath = os.path.join("results", json_name.strip(".json"))
        # os.makedirs(outpath, exist_ok=True)
        # for key, value in difference.items():
        #     with open(os.path.join(outpath, f"{key}.json"), "w") as f:
        #         json.dump(value, f, indent=2, ensure_ascii=False)

        _item = {
            "File Name": json_name,
        }
        for key, value in difference.items():
            _item.update({
                key: len(value) if not isinstance(value, float) else value
            })
        data.append(_item)
    
    # export report
    df = REPORT._process(data)
    df.to_csv("report.csv")

if __name__ == "__main__":
    # auto_json = read_json(os.path.join(AUTO_LABEL_PATH, TEST_JSON))
    # manual_json = read_json(os.path.join(MANUAL_LABEL_PATH, TEST_JSON))
    # compare_label(auto_json, manual_json)
    process_folder(AUTO_LABEL_PATH, MANUAL_LABEL_PATH)