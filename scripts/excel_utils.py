import os
import string
from typing import Any, List

import cv2
from xlsxwriter import Workbook


def insert_image_worksheet(
    worksheet,
    img_path: str,
    row_index: int,
    col_index: int,
    x_offset: int = 0,
    y_offset: int = 0,
    cell_width: int = 750,
    cell_height: int = 50,
    positioning: int = 2,
) -> Any:
    """
    Adding image into specified cell,
    try to fit scale image to fit with cell size.
    """

    if (img_path is None) or (img_path == ""):
        return

    # can not find it
    if not os.path.exists(img_path):
        return

    image_np = cv2.imread(img_path)
    h, w = image_np.shape[:2]
    scale = min(cell_width / w, cell_height / h)

    worksheet.insert_image(
        row_index,
        col_index,
        img_path,
        {
            "x_offset": x_offset,
            "y_offset": y_offset,
            "x_scale": scale,
            "y_scale": scale,
            "object_position": positioning,
        },
    )

    return


class Writer:
    def __init__(self, output_path: str):
        self.workbook = Workbook(output_path)
        self.dct_worksheets = {}

    def close(self):
        self.workbook.close()

    def add_work_sheet(self, sheet_name):
        worksheet = self.workbook.add_worksheet(sheet_name)
        self.dct_worksheets[sheet_name] = worksheet

    def add_column(
        self,
        column_index: int,
        sheet_name: str,
        cell_width: int,
        cell_height: int,
        datas: List,
        column_name: str,
        is_image: bool = False,
    ):
        # corresponding row character
        upper_cases = list(string.ascii_uppercase)
        index_character = upper_cases[column_index]

        worksheet = self.dct_worksheets[sheet_name]
        worksheet.set_column_pixels(column_index, column_index + 1, cell_width)

        # write column title
        worksheet.write(0, column_index, column_name)
        cell_format = self.workbook.add_format({"text_wrap": 1})

        # add row by row
        index = 1
        for data in datas:
            worksheet.set_row_pixels(index, cell_height)

            if not is_image:
                worksheet.write(
                    "%s%d" % (index_character, index + 1), data, cell_format
                )
            else:
                insert_image_worksheet(
                    worksheet,
                    data,
                    index,
                    col_index=column_index,
                    cell_width=int(0.9 * cell_width),
                    cell_height=int(0.9 * cell_height),
                )

            index += 1


if __name__ == "__main__":
    pass
