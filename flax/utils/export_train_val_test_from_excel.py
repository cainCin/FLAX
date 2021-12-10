import pandas as pd
import os
import glob
import re
import shutil


def main():
    # df = pd.read_excel(excel_path, header=0, index_col=0, engine='openpyxl')
    xl = pd.ExcelFile(excel_path)
    df = xl.parse("QR FINAL", header=0, index_col=0)
    df = df.fillna('')

    data_list = glob.glob(root_dir + "/*")
    data_list_sim = [
        re.sub(r"[\W\_\＿デデググブブドドズズダダパパババププ]", "", ".".join(datapath.split(".")[:-1]))
        for datapath in data_list
    ]
    # YYYY242167_1_FutureStage_岡部バルブ工業_発注書①_0
    # YYYY242167_1_FutureStage_岡部バルブ工業_発注書①_0
    # YYYY814903_2_【SMILE V_ラプラス_注文書】②_0
    # YYYY814903_2_【SMILE　V_ラプラス_注文書】②_0
    for i in range(len(df)):
        if len(df.iloc[i]['HW/ Reject']) > 0:
            continue
        filename = df.iloc[i]['file_name']
        datatype = df.iloc[i]['type']
        datapath = os.path.join(root_dir, filename)
        # print(df.iloc[i])
        if not os.path.isfile(datapath):
            if re.sub(r"[\W\_\＿デデググブブドドズズダダパパババププ]", "", ".".join(datapath.split(".")[:-1])) in data_list_sim:
                possible_path = data_list[data_list_sim.index(re.sub(r"[\W\_\＿デデググブブドドズズダダパパババププ]", "", ".".join(datapath.split(".")[:-1])))]
                # print('Might be', possible_name)
                if not os.path.isfile(possible_path):
                    print(possible_path)         
                
                    print(f"{filename}, {datatype}, {os.path.isfile(datapath)}")
            
            # print(df.iloc[i])
        else:
            possible_path = datapath

        #TODO: copy to corresponding
        target_split = [split for split in split_type if split in datatype][0]

        shutil.copy(possible_path, os.path.join(out_path, target_split))




    pass

if __name__ == '__main__':
    excel_path = r"D:\Workspace\cinnamon\code\prj\TRUSCO\Trusco_Prd_Wendy.xlsx"
    root_dir = r'D:\Workspace\cinnamon\code\prj\TRUSCO\QR all data'
    out_path = r'D:\Workspace\cinnamon\code\prj\TRUSCO\QR_split'
    os.makedirs(out_path, exist_ok=True)
    split_type = ['train', 'val', 'test']
    for split in split_type:
        os.makedirs(os.path.join(out_path, split), exist_ok=True)

    main()