# import sys
# sys.path.append(r"D:\Workspace\cinnamon\code\github\lib_rulebased")
from rulebased.document import Document
from rulebased.config.config import CONFIG
import os
# sys.path.append(r"D:\Workspace\cinnamon\code\dev\utilities")
from rulebased.utils.common_utils import imread, visualize, load_json
from utils.deloitte_utils import sort_textline, is_horizontal_overlap
import json
import glob
import numpy as np
import re
from rulebased.utils.common_utils import (
    compute_overlap, 
    compute_overlap_x, 
    compute_overlap_y, 
    common_elements,
    text_distance,
    find_region,
    extent_region,
    load_json
)

class Customize_Document(Document):

    def _process_single_in_table(self, anchor_textline, lst_textline, target_field):
        '''
        This function get a list of Textline object around the `anchor_textline` in the direction given in `target_field`

        If the candidate textline is found, the `target_field` is updated and return
        :param anchor_textline: Textline
            The anchor_textline contains the KEY of a KEY-VALUE pair.
        :param lst_textline: List
            Contain a list of Textline
        :param target_field: List
        [
             'field': Field
             'pattern': str (the 'pattern' is taken from Field.pattern)
        ]
        :return:
        target_field: List
        [
             'field': Field
             'pattern': str (the 'pattern' is taken from Field.pattern)
             'in_table': List ('in_table' contain a list of Textline objects expected to be VALUE)
        ]

        '''
        field = target_field['field']

        cfg = field.in_table_config
        priority_direction = cfg.get('direction', [])

        field = target_field['field']

        # cfg = field.out_table_config
        # priority_direction = cfg.get('direction', [])
        region_range = cfg.get('range', 500)
        region_extend_horizontal = cfg.get('horizontal_extend', 3)
        region_extend_vertical = cfg.get('vertical_extend', 3)
        intersect_threshold = cfg.get('intersect_threshold', 0.5)
        alignment = cfg.get('alignment', None)
        H, W = self.size[:2]

        if not cfg: 
            return None

        # TODO: check condition .a.k.a anchor textline in table
        if anchor_textline.table_id < 0: return None

        detected_candidates = []
        for idx, direction in enumerate(priority_direction):
            if direction is None:
                detected_candidates = [tl for tl in lst_textline
                                        if tl.cell_id == anchor_textline.cell_id 
                                            and tl.table_id == anchor_textline.table_id
                                            and tl.id != anchor_textline.id]

            else:
                # TODO: region range in the same table only
                if 'bottom' in direction:
                    region_range = max(self.list_table[anchor_textline.table_id].location[2][1] - anchor_textline.location[2][1], 0)
                elif 'right' in direction:
                    region_range = max(self.list_table[anchor_textline.table_id].location[2][0] - anchor_textline.location[2][0], 0)

                if anchor_textline.cell_id < 0:
                    best_kw = None
                else:
                    cell_contain = self.list_cell[anchor_textline.cell_id]
                    #TODO: verify if cell is well detected
                    cell_textline = [tl for tl in self.list_textline if tl.cell_id == anchor_textline.cell_id]
                    text = "".join([tl.text for tl in cell_textline])
                    best_kw = self._find_keyword(field, self.normalize_text(text))

                if best_kw is not None:     # cell is well detected
                    # TODO: region range in the same table only
                    if 'bottom' in direction:
                        region_range = max(self.list_table[anchor_textline.table_id].location[2][1] - cell_contain.location[2][1], 0)
                    elif 'right' in direction:
                        region_range = max(self.list_table[anchor_textline.table_id].location[2][0] - cell_contain.location[2][0], 0)

                    value_region = find_region(cell_contain.bbox, 
                                                direction, 
                                                region_range, 
                                                W, H)

                    if 'bottom' in direction: # extend on the horizontal
                        value_region = extent_region(value_region, [region_extend_horizontal, 0], W, H, alignment=alignment[idx])
                    elif 'right' in direction: # extend on vertical
                        value_region = extent_region(value_region, [0, region_extend_vertical], W, H, alignment=alignment[idx])
                else:   # use out_table config if possible
                    region_extend_horizontal = field.out_table_config.get('horizontal_extend', 3)
                    region_extend_vertical = field.out_table_config.get('vertical_extend', 3)
                    intersect_threshold = field.out_table_config.get('intersect_threshold', 0.5)
                    value_region = find_region(anchor_textline.bbox, 
                                                direction, 
                                                region_range, 
                                                W, H)

                    if 'bottom' in direction: # extend on the horizontal
                        value_region = extent_region(value_region, [region_extend_horizontal, 0], W, H, alignment=alignment[idx])
                    elif 'right' in direction: # extend on vertical
                        value_region = extent_region(value_region, [0, region_extend_vertical], W, H, alignment=alignment[idx])

                detected_candidates = [tl for tl in lst_textline if compute_overlap(value_region, tl.bbox) > intersect_threshold]

                #TODO: check alignment
                if len(detected_candidates) == 0:
                    continue
                elif best_kw is not None:  # check alignment in cell - textline must be in cell
                    detected_candidates = [tl for tl in detected_candidates if compute_overlap(value_region, tl.bbox) > 0.8]
                else:
                    if 'bottom' in direction:
                        #TODO: CASE right alignment
                        if "right" in alignment[idx]:
                            right_anchor = np.median([tl.bbox[2] for tl in detected_candidates])
                            left_anchor = np.min([tl.bbox[0] for tl in detected_candidates])
                        elif "left" in alignment[idx]:
                            #TODO: CASE left alignment
                            left_anchor = np.median([tl.bbox[0] for tl in detected_candidates])
                            right_anchor = np.max([tl.bbox[2] for tl in detected_candidates])

                        value_region[0] = min(left_anchor, anchor_textline.bbox[0])
                        value_region[2] = max(right_anchor, anchor_textline.bbox[2])
                    elif 'right' in direction:
                        #TODO: CASE right alignment
                        top_anchor = np.median([tl.bbox[1] for tl in detected_candidates])
                        #TODO: CASE left alignment
                        bottom_anchor = np.median([tl.bbox[3] for tl in detected_candidates])
                        value_region[1] = min(top_anchor, anchor_textline.bbox[1])
                        value_region[3] = max(bottom_anchor, anchor_textline.bbox[3])

                    
                    detected_candidates = [tl for tl in lst_textline if compute_overlap(value_region, tl.bbox) > 0.8]
                        



                # cell_contain = self.list_cell[anchor_textline.cell_id]
                # cell_neighbor = cell_contain.get_neighbor(direction, offset=None)
                # if cell_neighbor:
                #     cell_neighbor = cell_neighbor[0]
                #     detected_candidates = [tl for tl in lst_textline 
                #                             if tl.cell_id == cell_neighbor.id
                #                                 and tl.id != anchor_textline.id]

            # TODO: validation checking
            detected_candidates = [tl for tl in detected_candidates if field.is_valid(tl.text)]     # text condition
            

            if detected_candidates:
                target_field.update({'in_table': detected_candidates})
                return target_field

        return None

    def _process_single_out_table(self, anchor_textline, lst_textline, target_field):
        '''
        This function get a list of Textline object around the `anchor_textline` in the direction given in `target_field`

        .. note:: value_region: a location that are expected to contain VALUE

        .. note:: detected_candidates:
            a list of Textline object in the value_region

        :param anchor_textline: Textline
            The anchor_textline contains the KEY of a KEY-VALUE pair.
        :param lst_textline: List
            Contain a list of Textline
        :param target_field: list
        [
             'field': Field
             'pattern': str (the 'pattern' is taken from Field.pattern)
        ]
        :return:
        target_field: list
        [
             'field': Field
             'pattern': str
             'out_table': list => ('out_table' contain a list of Textline objects expected to be VALUE)
        ]

        '''
        field = target_field['field']

        cfg = field.out_table_config
        priority_direction = cfg.get('direction', [])
        region_range = cfg.get('range', 500)
        region_extend_horizontal = cfg.get('horizontal_extend', 50)
        region_extend_vertical = cfg.get('vertical_extend', 30)
        intersect_threshold = cfg.get('intersect_threshold', 0.5)
        alignment = cfg.get('alignment', None)

        if not cfg: 
            return None

        H, W = self.size[:2]

        detected_candidates = []
        for idx, direction in enumerate(priority_direction):
            value_region = find_region(anchor_textline.bbox, 
                                        direction, 
                                        region_range, 
                                        W, H)

            if 'bottom' in direction: # extend on the horizontal
                value_region = extent_region(value_region, [region_extend_horizontal, 0], W, H, alignment=alignment[idx])
            elif 'right' in direction: # extend on vertical
                value_region = extent_region(value_region, [0, region_extend_vertical], W, H, alignment=alignment[idx])

            detected_candidates = [tl for tl in lst_textline if compute_overlap(value_region, tl.bbox) > intersect_threshold]

            detected_candidates = [tl for tl in detected_candidates if field.is_valid(tl.text)]

            if detected_candidates:
                target_field.update({'out_table': detected_candidates})
                return target_field

        return None



class KeyValue:
    def __init__(self, config=CONFIG, FULL_KEYWORDS=[]):
        self.config = config
        self.FULL_KEYWORDS = FULL_KEYWORDS
        pass

    def process(self, image, la_ocr_data, table_data):
        lc_ocr_data = sort_textline(la_ocr_data)
        sample_prj = Customize_Document(image, la_ocr_data, table_data, config=self.config)
        sample_prj.find_keyword_pattern()
        
        sample_prj.process_in_table()
        sample_prj.process_out_table()

        #TODO: fetch all candidates
        lst_target_fields = [tl for tl in sample_prj.list_textline if len(tl.target_fields) > 0]
        

        #TODO: For each table, fetch only 1 keywords
        filt_target_fields = []
        for field in sample_prj.list_field:
            #TODO: find keywords for each fields in table first
            table_best_kw = []
            for table_idx, table_content in enumerate(sample_prj.list_table):

                #TODO: fetch keywords in corresponding table
                table_kws = [tl for tl in lst_target_fields if tl.table_id == table_idx]

                #TODO: fetch all possible keywords for current field
                field_kws = []
                for tl in table_kws:
                    for target_field in tl.target_fields:
                        if target_field.get('field') == field:
                            field_kws.append((tl, target_field))

                #TODO: fetch patterns to output
                table_patterns = [item for item in field_kws if item[1].get('pattern')]
                table_best_kw.extend(table_patterns)
                field_kws = [item for item in field_kws if item[1].get('pattern') is None]


                #TODO: limit keywords with the best threshold from FULL_KEYWORDS
                '''
                Textline should be best matching with keywords for this fields: max_dist(kw, field) == max_dist(kw, all_field)
                '''
                if not self.FULL_KEYWORDS:
                    best_field_kws = field_kws
                else:
                    best_field_kws = []
                    for field_kw, field_target  in field_kws:
                        best_similarity = max([text_distance(x, field_kw.text)[-1] for x in FULL_KEYWORDS])
                        if field_target.get('dist_text') < best_similarity: continue
                        best_field_kws.append((field_kw, field_target))

                #TODO: filtering empty values
                best_field_kws = [item for item in best_field_kws if item[1].get('pattern') is not None \
                                                                    or item[1].get('in_table') is not None \
                                                                    or item[1].get('out_table') is not None 
                                                                    ]

                ##TODO: filtering not on top rows of table <=====================
                filt_best_field_kws = best_field_kws


                #TODO: get only 1 best keyword / field / table based on the priority in keyword list
                best_field_kw = [min(filt_best_field_kws, key=lambda x: (
                                                                -x[1].get('dist_match'), 
                                                                field.list_keyword.index(x[1].get('kw'))
                                                                )
                                    )
                                ] \
                                if filt_best_field_kws else filt_best_field_kws
                
                print(f"{table_idx} - {field.field_name} - {[kw.text for (kw, field_target) in best_field_kw]}")
                table_best_kw.extend(best_field_kw)
            
            #TODO: IN CASE empty in table = > find out table
            if len(table_best_kw) == 0:
                #TODO: fetch keywords out side table
                table_kws = [tl for tl in lst_target_fields if tl.table_id < 0]

                #TODO: fetch all possible keywords for current field
                field_kws = []
                for tl in table_kws:
                    for target_field in tl.target_fields:
                        if target_field.get('field') == field:
                            field_kws.append((tl, target_field))

                #TODO: fetch patterns to output
                table_patterns = [item for item in field_kws if item[1].get('pattern')]
                table_best_kw.extend(table_patterns)
                field_kws = [item for item in field_kws if item[1].get('pattern') is None]

                #TODO: limit keywords with the best threshold from FULL_KEYWORDS
                if not self.FULL_KEYWORDS:
                    best_field_kws = field_kws
                else:
                    best_field_kws = []
                    for field_kw, field_target in field_kws:
                        best_similarity = max([text_distance(x, field_kw.text)[-1] for x in FULL_KEYWORDS])
                        if field_target.get('dist_text') < best_similarity - 0.01: continue
                        best_field_kws.append((field_kw, field_target))

                #TODO: filtering empty values
                best_field_kws = [item for item in best_field_kws 
                                    if item[1].get('pattern') is not None \
                                    or item[1].get('in_table') is not None \
                                    or item[1].get('out_table') is not None 
                                ]

                #TODO: get only 1 best keyword / field / table based on the priority in keyword list
                best_field_kw = [min(best_field_kws, key=lambda x: (
                                                        -x[1].get('dist_match'), 
                                                        field.list_keyword.index(x[1].get('kw'))
                                                        )
                                    )
                                ] \
                                if best_field_kws else best_field_kws
                
                print(f"{-1} - {field.field_name} - {[kw.text for (kw, field_target) in best_field_kw]}")
                table_best_kw.extend(best_field_kw)

            #TODO: export to output
            filt_target_fields.extend(table_best_kw)
 
        #TODO: to cassia
        out = []
        for tl, target_candidate in filt_target_fields:
            #TODO: verify if target is used
            current_used_location = [item.get('location') for item in out]
            if tl.location in current_used_location: continue

            #TODO: checkif it is a pattern ==> value
            if target_candidate.get("pattern"):
                out.append({
                    "text": tl.text,
                    "type": target_candidate.get('field').field_name,
                    "key_type": "value",
                    "location": tl.location,
                })
            
            else:
                #TODO: append key info
                out.append({
                    "text": tl.text,
                    "type": target_candidate.get('field').field_name,
                    "key_type": "key",
                    "location": tl.location,
                })

                #TODO: fetch intable
                in_table_candidate = sorted(target_candidate.get('in_table', []), 
                                        key=lambda x: (
                                            x.location[0][1] - tl.location[0][1], 
                                            x.location[0][0] - tl.location[0][0])
                                        )
                in_table_values = []
                for i, value in enumerate(in_table_candidate):
                    if value.location in current_used_location: continue

                    # TODO: check line condition
                    valid = True
                    list_hints = [item for item in sample_prj.list_textline if \
                            is_horizontal_overlap(item.location, value.location, thres=0.3) and \
                            item.table_id == value.table_id]
                    text_hints = "".join([item.text for item in sorted(list_hints, key=lambda tl: tl.bbox[0])]).replace(" ","")

                    for e_kw in target_candidate.get('field').value_exception_keyword:
                        if e_kw in re.sub("[\(<].*[\)>]", "", text_hints):
                            if len(e_kw) < 2:  # in case too short exception keyword, we need to check every textline to match value
                                valid = not any([re.sub("\W", "", item.text) == e_kw for item in list_hints])
                            else:
                                valid = False
                            if not valid:       # find unvalid pattern => STOP and skip this value
                                break

                                
                    if not valid: continue
                    # print(f"{value.text} ============= ")

                    in_table_values.append({
                        "text": value.text,
                        "type": target_candidate.get('field').field_name,
                        "key_type": "value",
                        "location": value.location,
                    })

                    if i + 1 >= target_candidate.get('field').max_values:   # take only max_values values
                        break
                out.extend(in_table_values)
                if len(in_table_values) > 0: continue


                #TODO: fetch out table
                out_table_candidate = sorted(target_candidate.get('out_table', []), 
                                        key=lambda x: (
                                            x.location[0][1] - tl.location[0][1],
                                            x.location[0][0] - tl.location[0][0],
                                        )
                                    )
                for i, value in enumerate(out_table_candidate):
                    if value.location in current_used_location:     # SKIP determined values
                        continue
                    #TODO: check condition: table and value shouldn't both in tables ==> otherwise, it should be in table part
                    if tl.cell_id > -1: continue    # if key is in table, it should be skipped

                    # TODO: check line condition
                    valid = True
                    list_hints = [item for item in sample_prj.list_textline 
                                    if is_horizontal_overlap(item.location, value.location, thres=0.3)
                                ]
                    text_hints = "".join([item.text for item in sorted(list_hints, key=lambda tl: tl.bbox[0])]).replace(" ","")

                    for e_kw in target_candidate.get('field').value_exception_keyword:
                        if e_kw in re.sub("[\(<].*[\)>]", "", text_hints):
                            if len(e_kw) < 2:  # in case too short exception keyword, we need to check every textline to match value
                                valid = not any([re.sub("\W", "", item.text) == e_kw for item in list_hints])
                            else:
                                valid = False
                            if not valid:
                                break
                                
                    if not valid: continue

                    out.append({
                        "text": value.text,
                        "type": target_candidate.get('field').field_name,
                        "key_type": "value",
                        "location": value.location,
                    })
                    if i + 1 >= target_candidate.get('field').max_values:
                        break
        return out

