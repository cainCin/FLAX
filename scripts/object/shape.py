import json
import math
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict

import cv2
import numpy as np
from shapely import Polygon, MultiPolygon

from object_cls import ObjectClass, AutoObjectClass


@dataclass
class Shape:
    polygon: np.ndarray  # (n, 2)
    bounding_box: np.ndarray  # (4,2)
    rotated_bounding_box: np.ndarray  # (4,2)
    cls: ObjectClass

    def to_obb_str(self, expected_size: Tuple) -> str:
        line_str = [str(self.cls.value)]
        w, h = expected_size[:2]

        line_floats = []
        cut_off = False
        for point in self.rotated_bounding_box.astype(float):
            x, y = point
            # print(x, y, w, h)

            if x < 0 or y < 0 or x > w or y > h:
                cut_off = True

            # assert 0 <= x <= expected_size[0], print(self.rotated_bounding_box)
            # assert 0 <= y <= expected_size[1], print(self.rotated_bounding_box)

            line_str += [str(x / w), str(y / h)]
            line_floats += [[x, y]]

        (x, y), (w, h), angle = cv2.minAreaRect(np.array(line_floats).astype(int))

        if cut_off:
            print(x, y, w, h, angle)

        return " ".join(line_str)

    def to_polygon_str(self, expected_size: Tuple) -> str:
        line_str = []
        for point in self.polygon.astype(int):
            x, y = point

            assert 0 <= x <= expected_size[0], print(self.polygon)
            assert 0 <= y <= expected_size[1], print(self.polygon)

            line_str += [str(x), str(y)]

        line_str += [str(self.cls.value), "0"]
        return " ".join(line_str)

    def to_horizontal_str(self, expected_size: Tuple) -> str:
        # Format: ()
        x1, y1 = self.bounding_box[0]
        x2, y2 = self.bounding_box[2]

        x_center = ((x1 + x2) / 2.) / expected_size[0]
        y_center = ((y1 + y2) / 2.) / expected_size[1]
        width = (x2 - x1 + 1) / expected_size[0]
        height = (y2 - y1 + 1) / expected_size[1]

        assert 0 <= x_center < 1, f"{x_center}"
        assert 0 <= y_center < 1, f"{y_center}"
        assert 0 < width < 1., f"{width}"
        assert 0 < height < 1., f"{height}"

        line_str = map(str, [self.cls.value, x_center, y_center, width, height])
        return " ".join(line_str)

    def intersect_with_polygon(self, another_polygon: np.ndarray) -> Optional[np.ndarray]:
        """Return the over"""
        polygon1 = Polygon(self.polygon).buffer(0)
        polygon2 = Polygon(another_polygon).buffer(0)

        intersection = polygon1.intersection(polygon2)
        if intersection.is_empty:
            return

        if isinstance(intersection, Polygon):
            coords = intersection.exterior.coords
            return np.array(coords, dtype=int)
        elif isinstance(intersection, MultiPolygon):
            coords_list = [
                np.array(singe_intersection.exterior.coords, dtype=int)
                for singe_intersection in intersection.geoms
            ]

            # descending order
            coords_list = sorted(coords_list, key=lambda elem: cv2.contourArea(elem))[::-1]
            coords_list = coords_list[0]

            # approximate
            peri = cv2.arcLength(coords_list, True)
            approx = cv2.approxPolyDP(coords_list, 0.002 * peri, True)

            return approx[:, 0, :].astype(int)
        else:
            return


class AutoShape:
    @staticmethod
    def from_label_file(label_file: str) -> List[Shape]:
        """Read shapes from label_file"""
        label_data: Dict = json.load(open(label_file, 'r'))
        shapes = label_data["shapes"]
        result: List[Shape] = []

        for shape in shapes:
            cls = AutoObjectClass.guess_object_class(shape['label'])
            if cls is None:
                continue

            _shape_type = shape['shape_type']
            points = np.array(shape['points'], dtype=int)
            if _shape_type in ['rectangle']:
                x_min, y_min, width, height = cv2.boundingRect(points[:, None, :])
                points = np.array([
                    [x_min, y_min],
                    [x_min + width, y_min],
                    [x_min + width, y_min + height],
                    [x_min, y_min + height]
                ])
            elif _shape_type in ['circle']:
                center = (int(points[0][0]), int(points[0][1]))
                radius = int(
                    math.sqrt(
                        (points[0][0] - points[1][0]) ** 2
                        + (points[0][1] - points[1][1]) ** 2
                    )
                )

                n_sample = 15
                points = []
                for i in range(n_sample):
                    x = center[0] + radius * math.cos(i * 2 * math.pi / n_sample)
                    y = center[1] + radius * math.sin(i * 2 * math.pi / n_sample)
                    points += [(x, y)]
                points = np.array(points)  # (n, 2)
            elif _shape_type in ["polygon"]:
                points = np.array(shape['points'], dtype=int)  # (n, 2)
            else:
                raise Exception(f"Not implemented shape-type: {_shape_type} error!")

            #
            norm_shape = AutoShape.from_polygon(points, cls)
            if norm_shape is not None:
                result += [norm_shape]

        return result

    @staticmethod
    def from_polygon(polygon: np.ndarray, cls: ObjectClass) -> Optional[Shape]:
        n_points = polygon.shape[0]
        if n_points < 2:
            print(f"Expected at least 2 points but got {n_points} points!")
            return None
        polygon_int = polygon.astype(int)
        polygon_int_squeeze = polygon_int[:, None, :]

        # horizontal bounding box
        hx_min, hy_min, hwidth, hheight = cv2.boundingRect(polygon_int_squeeze)
        hx_max = hx_min + hwidth
        hy_max = hy_min + hheight
        hbox_points = np.array([
            [hx_min, hy_min],
            [hx_max, hy_min],
            [hx_max, hy_max],
            [hx_min, hy_max]
        ]).astype(int)

        # rotated bounding box
        rotated_rect = cv2.minAreaRect(polygon_int_squeeze)

        # rotate large angle
        if rotated_rect[2] > 45:
            rotated_rect = (
                rotated_rect[0],
                (rotated_rect[1][1], rotated_rect[1][0]),
                90 + rotated_rect[2],
            )
        rotated_box_points = cv2.boxPoints(rotated_rect).astype(int)  # tl, tr, br, bl

        return Shape(polygon_int, hbox_points, rotated_box_points, cls)


    @staticmethod
    def from_yolo_bbox_line(yolo_bbox_line: str, image_width: int, image_height: int) -> Optional[Shape]:
        cls, x_center, y_center, width, height = yolo_bbox_line.split(" ")
        width = float(width) * image_width
        height = float(height) * image_height
        x_min = float(x_center) * image_width - width / 2
        y_min = float(y_center) * image_height - height / 2
        points = np.array([
            [x_min, y_min],
            [x_min + width, y_min],
            [x_min + width, y_min + height],
            [x_min, y_min + height]
        ])
        return AutoShape.from_polygon(points, ObjectClass(int(cls)))