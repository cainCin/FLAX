from typing import List, Dict
from .location_utils import sort_textlines, get_distance, is_horizontal_overlap

def group_by_line(
    list_textlines: List[Dict],
    distance_threshold: float = 2.0,
    by_formalkey: bool = False,
) -> List[List[Dict]]:
    # sort textlines by y coordinate
    list_textlines = sort_textlines(list_textlines)

    # group textlines by line
    groups = []

    for textline in list_textlines:
        if len(groups) == 0:
            groups.append([textline])
            continue
        try:
            
            if by_formalkey and is_horizontal_overlap(groups[-1][-1]['location'], textline['location'], thres=0.5) and (groups[-1][-1]['type'] == textline['type']):
                groups[-1].append(textline)
            # elif (is_horizontal_overlap(groups[-1][-1]['location'], textline['location'], thres=0.5)) \
            #     and (get_distance(groups[-1][-1]['location'], textline['location'], axis='horizontal') < distance_threshold):
            #     groups[-1].append(textline)
            else:
                groups.append([textline])
        except Exception as e:
            import pdb; pdb.set_trace()
        
    return groups
