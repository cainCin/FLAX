from typing import List, Dict
import numpy as np
import cv2
from functools import cmp_to_key


def is_horizontal_overlap(
    loc1: List[tuple],
    loc2: List[tuple],
    thres: float = 0.3,
    vertical_offset: float = 0.0,
) -> bool:
    """Description: Verifying horizontal alignment between 2 locations
    Args:
        loc1 (List[tuple]): input location 1
        loc2 (List[tuple]): input location 2
        thres (float): tolerant threshold for decision
        vertical_offset (float): additional offset of second location in this alignment
            (calculate relatively with location height)

    Returns:
        Return True if horizontal overlapping, otherwise return False
    """
    # get first location attributes
    x1_1, y1_1, w1, h1 = cv2.boundingRect(np.array(loc1))
    # x1_2 = x1_1 + w1  # TODO: 'x1_2' is assigned to but never used
    y1_2 = y1_1 + h1

    # get second location attributes
    x2_1, y2_1, w2, h2 = cv2.boundingRect(np.array(loc2))
    # x2_2 = x2_1 + w2  # TODO: 'x2_2' is assigned to but never used
    y2_2 = y2_1 + h2

    # add offset to second location attributes
    y2_1 = y2_1 + vertical_offset * h2
    y2_2 = y2_2 + vertical_offset * h2

    # verify by horizontal intersection
    h_intersect = max(0, min(y1_2, y2_2) - max(y2_1, y1_1))
    isHorizontal = h_intersect > min(h1, h2) * thres

    return isHorizontal


def is_vertical_overlap(
    loc1: List[tuple], loc2: List[tuple], thres: float = 0.3
) -> bool:
    """Verifying vertical alignment between 2 locations
    Args:
        loc1 (List[tuple]): input location 1
        loc2 (List[tuple]): input location 2
        thres (float): tolerant threshold for decision

    Returns:
        Return True if vertical overlapping, otherwise return False
    """
    # get first location attributes
    x1_1, y1_1, w1, h1 = cv2.boundingRect(np.array(loc1))
    x1_2 = x1_1 + w1
    # y1_2 = y1_1 + h1  # TODO: 'y1_2' is assigned to but never used

    # get second location attributes
    x2_1, y2_1, w2, h2 = cv2.boundingRect(np.array(loc2))
    x2_2 = x2_1 + w2
    # y2_2 = y2_1 + h2  # TODO: 'y2_2' is assigned to but never used

    # verify by vertical intersection
    v_intersect = max(0, min(x1_2, x2_2) - max(x2_1, x1_1))
    isVertical = v_intersect > min(w1, w2) * thres

    return isVertical


def iou(loc1: List[int], loc2: List[int], iou_type: int = 0) -> float:
    """Computes the intersection over union (IoU) of two regions.

    Args:
        loc1: A list of four integers representing the (x, y, width, height) coordinates of the first region.
        loc2: A list of four integers representing the (x, y, width, height) coordinates of the second region.
        iou_type: An integer indicating the type of IoU to calculate. Only the following three types are supported:
            0: The IoU of the two regions.
            1: The ratio of intersection to the smaller area of the two regions.
            2: The ratio of intersection to the area of the first region.

    Returns:
        A float value between 0 and 1 representing the IoU of the two regions.

    Raises:
        AssertionError: If the iou_type argument is not one of the supported values.

    Examples:
        >>> loc1 = [0, 0, 10, 10]
        >>> loc2 = [5, 5, 10, 10]
        >>> iou(loc1, loc2)
        0.14285714285714285
    """

    assert iou_type in [
        0,
        1,
        2,
    ], "Only support 0: origin iou, 1: intersection / min(area), 2: oversegment on loc1"
    if isinstance(loc1[0], list|tuple):
        x1, y1, w1, h1 = cv2.boundingRect(np.array(loc1).astype(int))
    else:
        x1, y1, w1, h1 = loc1
    if isinstance(loc2[0], list|tuple):
        x2, y2, w2, h2 = cv2.boundingRect(np.array(loc2).astype(int))
    else:
        x2, y2, w2, h2 = loc2

    # intersection
    x_left = max(x1, x2)
    x_right = min(x1 + w1, x2 + w2)
    y_top = max(y1, y2)
    y_bot = min(y1 + h1, y2 + h2)

    inter = max(0, x_right - x_left) * max(0, y_bot - y_top)

    union = w1 * h1 + w2 * h2 - inter
    if iou_type == 1:
        union = min(w1 * h1, w2 * h2)
    elif iou_type == 2:
        union = w1 * h1
    if union > 0:
        iou = inter / union
    else:
        iou = 0
    return iou


def compare_location(textline1: Dict, textline2: Dict) -> int:
    """Ordering 2 textlines by top-bottom, left-right
    Args:
        textline1 (Dict): input textline 1 with location information
        textline2 (Dict): input textline 2 with location information
    Returns:
        The difference between the left coordinate of textline1 and textline2 if they overlap horizontally,
             otherwise the difference between the top coordinate of textline1 and textline2.
    Examples:
        >>> textline1 = {'location': [10, 20, 100, 50]}
        >>> textline2 = {'location': [20, 40, 80, 30]}
        >>> compare_location(textline1, textline2)
        -10
    """
    # get textline location attributes
    x1, y1, w1, h1 = cv2.boundingRect(np.array(textline1.get("location")).astype(int))
    x2, y2, w2, h2 = cv2.boundingRect(np.array(textline2.get("location")).astype(int))

    # compare textline location
    if is_horizontal_overlap(
        textline1.get("location"), textline2.get("location"), thres=0.5
    ):
        return x1 - x2

    else:
        return y1 - y2


def get_distance(
    current_location: List[tuple], next_location: List[tuple], axis: str = "horizontal"
) -> float:
    """Get relative distance between 2 textlines (based on the maximum textline height)

    Args:
        current_location (List[tuple]): The location of the current textline.
        next_location (List[tuple]): The location of the next textline.
        axis (str): The axis along which to measure the distance.
            Can be either "horizontal" or "vertical". Defaults to "horizontal".

    Returns:
        The relative distance between the two textlines.

    Raises:
        AssertionError: If the value of axis is not "horizontal" or "vertical".

    Examples:
        >>> current_location = [(10, 20), (50, 20), (50, 40), (10, 40)]
        >>> next_location = [(60, 30), (100, 30), (100, 60), (60, 60)]
        >>> get_distance(current_location, next_location, axis='horizontal')
        1.0
    """
    assert axis in ["horizontal", "vertical"], f"axis {axis} not supported"
    # get absolute distance
    if axis == "horizontal":
        distance = (
            np.array(next_location).min(axis=0)[0]
            - np.array(current_location).max(axis=0)[0]
        )
    else:
        distance = (
            np.array(next_location).min(axis=0)[1]
            - np.array(current_location).max(axis=0)[1]
        )

    # get location attributes
    x1, y1, w1, h1 = cv2.boundingRect(np.array(current_location))
    x2, y2, w2, h2 = cv2.boundingRect(np.array(next_location))
    h = max(h1, h2)

    return float(distance) / h


def sort_textlines(layout_output: List[Dict]) -> List[Dict]:
    """Sorts a list of textlines by their location.

    Args:
        layout_output (list[dict]): A list of textlines follow std lib-layout format

    Returns:
        A sorted list of textlines, ordered from top to bottom and left to right.

    """
    return sorted(layout_output, key=cmp_to_key(compare_location))


def get_athena_bbox(shape_attr: dict):
    """Get bounding box from shape attributes
    Args:
        shape_attr (dict): shape attributes
    Returns:
        bounding box of shape attributes
    """
    if shape_attr["name"] == "rect":
        x = shape_attr["x"]
        y = shape_attr["y"]
        w = shape_attr["width"]
        h = shape_attr["height"]
    elif shape_attr["name"] == "polygon":
        x, y, w, h = cv2.boundingRect(np.array(
            [(int(x), int(y)) for x,y in zip(shape_attr["all_points_x"], shape_attr["all_points_y"])]
        ))
    return x,y,w,h