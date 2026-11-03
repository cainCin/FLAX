"""Script to generate report"""
import glob
import logging
import os
import shutil
import tempfile
import time
from os import environ as env

import json
import pandas as pd
from openpyxl import load_workbook
from typing import List

import click
from excel_utils import Writer
import cv2
import numpy as np


logging.basicConfig(
    level=env.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def _get_key_name(item):
    if "formal_key" in item:
        if isinstance(item["formal_key"], str):
            return item["formal_key"]
        elif isinstance(item["formal_key"], list):
            return item["formal_key"][0]
    elif "type" in item:
        return item["type"]




class REPORT(object):

    @staticmethod
    def _read_snippet(image, location: List[tuple], margin=0) -> str:
        """
        Read the snippet from the bbox
        """
        if location is None:
            return ""
        
        

        image_origin_h, image_origin_w = image.shape[:2]

        x_min, y_min, width, height = cv2.boundingRect(np.array(location))
        
        x_max = x_min + width
        y_max = y_min + height

        # image_bbox_ = read_snippet(image, [(x_min, y_min), (x_max, y_max)], margin=margin)
        x_min_w_margin = max(0, x_min - margin)
        y_min_w_margin = max(0, y_min - margin)
        y_max_w_margin = min(y_max + margin, image_origin_h)
        x_max_w_margin = min(x_max + margin, image_origin_w)        

        image_bbox_ = image[
            y_min_w_margin:y_max_w_margin,
            x_min_w_margin:x_max_w_margin,
        ].copy()

        h, w = image_bbox_.shape[:2]
        if h > 64 and w > 64:
            rt = min(64.0/image_bbox_.shape[0], 64.0/image_bbox_.shape[1])
            image_bbox_ = cv2.resize(
                image_bbox_,
                (int(rt*image_bbox_.shape[1]), int(rt*image_bbox_.shape[0])),
                interpolation=cv2.INTER_LINEAR,
            )

        return image_bbox_

    @staticmethod
    def export_sheet(df, output_excel, sheet_name):
        """Add new sheet with DataFrame data"""

        # If file exists, preload it
        book = None
        if os.path.exists(output_excel):
            book = load_workbook(output_excel)

        writer = pd.ExcelWriter(output_excel, engine="openpyxl")

        if book is not None:
            writer.book = book

        df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
        writer.close()
    

    @staticmethod
    def export_sheet_with_snippet(df, output_excel, sheet_name):
        # create workbook
        writer = Writer(output_excel)

        # add worksheet
        writer.add_work_sheet(sheet_name)
        for column_id, column in enumerate(df.columns):
            data_column = df[column].tolist()

            is_image = "snippet" in column
            if is_image:
                cell_width = 300
            else:
                cell_width = 100
            writer.add_column(
                column_index=column_id,
                sheet_name=sheet_name,
                datas=data_column,
                column_name=column,
                is_image=is_image,
                cell_width=cell_width,
                cell_height=100,
            )
        
        writer.close()

    

    @classmethod
    def process(cls, input_path, output_path, sheet_name="NON-TUNING" , report_type="kv", output_type="xlsx", classes=None):
        for filename in glob.glob(os.path.join(input_path, "*")):
            tmp_dir = tempfile.mkdtemp()
            name = os.path.basename(filename)
            _output_path = os.path.join(output_path, name + ".xlsx")
            data = cls._load_data(filename, report_type=report_type, classes=classes, tmp_dir=tmp_dir)
            df = cls._process(data)

            if "xls" in _output_path[-4:]:
                cls.export_sheet_with_snippet(df, _output_path, sheet_name)
            else:
                df.to_csv(_output_path)

            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
    
    @staticmethod
    def _load_data(input_data, report_type, classes=None, tmp_dir="."):
        # input_list = glob.glob(os.path.join(input_data, f"{report_type}.json"))
        input_list = [
            os.path.join(input_data, f"{report_type}.json")
        ]
        data = list()
        for output_path in input_list:
            filename = output_path.split(os.sep)[-2]
            image_data = cv2.imread(
                os.path.join(os.path.dirname(output_path), "image.jpg")
            )
            # label_path = os.path.join(
            #     "/mnt/c/Users/Cain/Documents/data/TA/bs_/tpcofo4405_tepco_accenture_flax_poc_1",
            #     "label",
            #     f"{filename}.json"
            # )
            # from athena.fileio import load_athena_json
            # output = load_athena_json(label_path, only=None)
            output = json.load(open(output_path, "r", encoding="utf-8"))
            data_out = []
            if len(output) > 0 and isinstance(output[0], list):
                output = sum(output, [])

            for index, item in enumerate(output):
                if classes is not None and _get_key_name(item) not in classes:
                    continue
                # import pdb; pdb.set_trace()
                # making basic info
                info = {
                    "File Name": filename,
                    "Formal Key": _get_key_name(item),
                    "AIOCR": item["text"],
                }
                if "key_type" in item:
                    info.update({
                        "Key Type": item["key_type"]
                    })

                # update additional infos
                for k,v in item.items():
                    if k in ["formal_key", "key_type", "text", "type", "OCR"]:
                        continue
                    elif isinstance(v, str):
                        info.update({
                            k: v
                        })
                    elif isinstance(v, float):
                        info.update({
                            k: str(v)
                        })
                    elif k == "location":
                        snippet = REPORT._read_snippet(image_data, v)
                        snippet_path = os.path.join(tmp_dir, f"{filename}_{index}.png")
                        cv2.imwrite(snippet_path, snippet)

                        info.update({
                            'snippet': snippet_path
                        })

                        # dump json_str for location
                        info.update({
                            k: json.dumps(v)
                        })

                    # elif isinstance(v, List):
                    #     info.update({
                    #         k: v
                    #     })
                
                data_out.append(info)
                    
            data.extend(data_out)
        
        return data

    def _process(data):
        """Main logic to generate DataFrame"""
        # Convert data to DataFrame
        df: pd.DataFrame = pd.DataFrame.from_records(data)

        return df



def get_pipeline_stages(result_folder):
    """Check the available result files in result folder"""
    json_results = glob.glob(f"{result_folder}/**/*.json", recursive=True)
    stages = set(os.path.splitext(os.path.basename(item))[0] for item in json_results)
    return list(stages)


def generate_report(result_folder, report_folder, classes=None):
    """Generate report and failure pattern for flax result

    line_keys: a list of key for line-report, you can input:
    1) "all", [default] generate line-report for all keys found in current dataset,
    use this when you would like to extract all keys with line-idx in report,
    but the order of keys would be sorted by their name,
    if you would like to set a specific order of keys, please use the second option.
    2) List, A list with specified keys with your preferred order, e.g. ["company_names", ...]
    3) None, disable line-report
    """

    # Generate report
    # TODO: When classes is not None, generate report with those classes only
    rp = REPORT()
    rp.process(result_folder, f"{report_folder}", report_type="kv", classes=classes)


@click.command()
@click.option("--result_folder", "-r", required=True, help="Path to pipeline result folder")
@click.option("--report_folder", "-o", help="Path to output directory")
def main(result_folder, report_folder, label_folder=''):
    start = time.time()

    logger.info("GENERATING REPORT...")

    generate_report(result_folder, report_folder)

    logger.info("FINISHED GENERATING REPORT...")

    total_runtime = (time.time() - start) / 60

    if total_runtime > 60:
        total_runtime = f"{(total_runtime / 60):.3f} HOURS"
    else:
        total_runtime = f"{total_runtime:.3f} MINUTES"

    logger.info(f"DONE! ESTIMATED RUN TIME: {total_runtime}")


if __name__ == "__main__":
    main()
