import glob, os

from PIL.Image import Image
# from layout import JeffLayout as LAYOUT
from layout import DcLayout as LAYOUT
from ocr import CannetOCR as OCR
from table import Tee as TABLE
from rulebased.core import KeyValue as KV 
from utils.basic_utils import imread, visualize 
import cv2
import numpy as np
import torch
from utils.athena_utils import convert_cassia_to_athena

import sys
sys.path.append(r"D:\Workspace\cinnamon\code\github\FLAX")
# from configs.rule_configs import * # name_vessel, NOR

_default_config = {
    'pretrain': {
        # 'layout': "models/layout/JeffLayout_print_handwritting_general.pth",
        'layout': r"D:\Workspace\cinnamon\code\github\FLAX\models\layout\DcLayout_Mix_v1.pth",
        'ocr': r"D:\Workspace\cinnamon\code\github\FLAX\models\ocr\ocr_cannetOCR_20190918_normalizePhase2_charset4685.pt",
        'table': r"D:\Workspace\cinnamon\code\github\FLAX\models\table\ocean.t7"
    },
    'config': {
        # 'layout': "configs/layout_config.yaml",
        # 'rulebased':[
        #     name_vessel,
        #     NOR,
        #     commenced_discharging,
        #     commenced_loading,
        #     completed_discharging,
        #     completed_loading,
        # ]
    }
}

from table.preprocessing.base import TablePreprocessModel
deskew_model = TablePreprocessModel('fftdeskew')


OUT_PATH = 'tmp'
os.makedirs(OUT_PATH, exist_ok=True)

def deskew(img):
    preprocess_output = deskew_model.process(img)[0]
    wimg = preprocess_output.pop("output")
    return wimg

import hashlib
def gen_checksum(image_path):
    with open(image_path, 'rb') as fi:
        checksum = hashlib.sha256(fi.read()).hexdigest()

    return checksum


class FLAX_AI:
    def __init__(self, config=_default_config):
        self.__dict__.update(config)
        #TODO: init AI models
        self.layout = LAYOUT(weights_path=self.pretrain.get('layout'))
        self.ocr = OCR(self.pretrain.get('ocr'))
        self.table = TABLE(self.pretrain.get('table'))
        # self.kv = KV(config=self.config.get('rulebased'))



    def process(self, datapath):
        data_list = glob.glob(datapath + "/*")

        for image_path in data_list:
            print(image_path)
            try:
                image = imread(image_path)
                #TODO: deskew image
                image = deskew(image)
                layout_output = self.layout.process(image)
                table_output = self.table.process(image)

                for item in layout_output:
                    x,y,w,h = cv2.boundingRect(np.array(item.get('location')))
                    crop_image = image[y:y+h, x:x+w]
                    item.update(self.ocr.process(crop_image))

                
                # kv_output = self.kv.process(image, la_ocr_data=layout_output, table_data=table_output)

                visualize(image, label=[], flax=layout_output, table=table_output).save(os.path.basename(image_path))

                #TODO: export
                store_image_path = os.path.join(OUT_PATH, os.path.basename(image_path))
                filename = ".".join(os.path.basename(image_path).split(".")[:-1])
                visualize(image).save(store_image_path)
                checksum = gen_checksum(store_image_path)
                convert_cassia_to_athena(layout_output, 
                    filename=os.path.basename(image_path), 
                    output=os.path.join(OUT_PATH, filename + ".json"), 
                    checksum=checksum)

            
            except Exception as e:
                print("Error:=========== \n", str(e))
            finally:
                torch.cuda.empty_cache()


if __name__ == "__main__":
    datapath = "samples"
    # datapath = r"D:\Workspace\cinnamon\code\prj\TRUSCO\QR_split\val"
    FLAX_AI().process(datapath)
    pass