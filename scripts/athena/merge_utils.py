from typing import List, Dict
import copy
import cv2
import numpy as np

def merge_group_textlines(
    groups: List[List[Dict]],
) -> List[Dict]:
    
    out = []
    for group in groups:
        if len(group) == 1:
            out.extend(group)
        else:
            new_item = copy.deepcopy(group[0])
            x, y, w, h = cv2.boundingRect(
                np.array(sum([item['location'] for item in group], []))
            )
            new_item['location'] = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
            new_item['text'] = ''.join([item['text'] for item in group])
    
            out.append(new_item)
    
    return out
