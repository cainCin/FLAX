"""Script to generate report"""
import glob
import logging
import os
import time
from os import environ as env

import json
import pandas as pd
from openpyxl import load_workbook
from typing import List

import click


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
    

    @classmethod
    def process(cls, input_path, output_path, sheet_name="NON-TUNING" , report_type="kv", output_type="xlsx", classes=None):
        data = cls._load_data(input_path, report_type=report_type, classes=classes)
        df = cls._process(data)

        if "xls" in output_path[-4:]:
            cls.export_sheet(df, output_path, sheet_name)
        else:
            df.to_csv(output_path)
    
    
    @staticmethod
    def _load_data(input_data, report_type, classes=None):
        input_list = glob.glob(os.path.join(input_data, "*", f"{report_type}.json"))
        data = list()
        for output_path in input_list:
            filename = output_path.split(os.sep)[-2]
            output = json.load(open(output_path, "r", encoding="utf-8"))
            data_out = []
            if len(output) > 0 and isinstance(output[0], list):
                output = sum(output, [])
            for item in output:
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
                    elif isinstance(v, List):
                        info.update({
                            k: v
                        })
                
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
    rp.process(result_folder, f"{report_folder}/test.xlsx", report_type="kv", classes=classes)


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
