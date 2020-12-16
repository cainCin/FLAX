import glob, os
from layout import JeffLayout as LAYOUT
from ocr import CannetOCR as OCR
from table import Tee as TABLE
from rulebased.core import KeyValue as KV 
from utils.basic_utils import imread, visualize 
import cv2
import numpy as np
import torch

import sys
sys.path.append(r"D:\Workspace\cinnamon\code\github\FLAX")
from configs.rule_configs import * # name_vessel, NOR

_default_config = {
    'pretrain': {
        'layout': "models/layout/JeffLayout_print_handwritting_general.pth",
        'ocr': "models/ocr/ocr_cannetOCR_20190918_normalizePhase2_charset4685.pt",
        'table': "models/table/ocean.t7"
    },
    'config': {
        'layout': "configs/layout_config.yaml",
        'rulebased':[
            name_vessel,
            NOR,
            commenced_discharging,
            commenced_loading,
            completed_discharging,
            completed_loading,
        ]
    }
}

class FLAX_AI:
    def __init__(self, config=_default_config):
        self.__dict__.update(config)
        #TODO: init AI models
        self.layout = LAYOUT(self.pretrain.get('layout'))
        self.ocr = OCR(self.pretrain.get('ocr'))
        self.table = TABLE(self.pretrain.get('table'))
        self.kv = KV(config=self.config.get('rulebased'))



    def process(self, datapath):
        data_list = glob.glob(datapath + "/*")

        for image_path in data_list:
            print(image_path)
            try:
                image = imread(image_path)
                layout_output = self.layout.process(image)
                table_output = self.table.process(image)

                for item in layout_output:
                    x,y,w,h = cv2.boundingRect(np.array(item.get('location')))
                    crop_image = image[y:y+h, x:x+w]
                    item.update(self.ocr.process(crop_image))

                
                kv_output = self.kv.process(image, la_ocr_data=layout_output, table_data=table_output)

                visualize(image, label=kv_output, flax=layout_output, table=table_output).save(os.path.basename(image_path))
            
            except Exception as e:
                print("Error:=========== \n", str(e))
            finally:
                torch.cuda.empty_cache()


if __name__ == "__main__":
    datapath = "samples"
    FLAX_AI().process(datapath)
    pass