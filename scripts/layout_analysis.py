import cv2
import os
from rapid_layout import RapidLayout, VisLayout
from file2image.get_images_from_path import get_images_from_path
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from typing import Tuple

# model_type类型参见上表。指定不同model_type时，会自动下载相应模型到安装目录下的。
layout_engine = RapidLayout(model_type="doclayout_docstructbench", conf_thres=0.2)

# img_url = "https://raw.githubusercontent.com/opendatalab/DocLayout-YOLO/refs/heads/main/assets/example/financial.jpg"
# img = imread_from_url(img_url)
font_height = 25
font = ImageFont.truetype("/mnt/c/Users/Cain/Documents/github/prj_flax/flax/utility/fonts/fonts-japanese-gothic.ttf", font_height)
# font_height = font.getsize("A")[1]  # Calculate the height u

# font_face = cv2.freetype.createFreeType2()
# font_face.loadFontData(fontFileName="/mnt/c/Users/Cain/Documents/github/prj_flax/flax/utility/fonts/fonts-japanese-gothic.ttf", id=0)


# DATAPATH = "/mnt/c/Users/Cain/Documents/data/docreader/Scan PDF/ブレーキ真空充填のための部品規格4(51ページ)_ori (1).pdf"
DATAPATH = "/mnt/c/Users/Cain/Documents/data/docreader/Scan PDF/image_hyo.pdf"
OUTPATH = "layout_analysis/rapid_layout"
os.makedirs(OUTPATH, exist_ok=True)


class CustomVisLayout(VisLayout):
    # @staticmethod
    # def draw_text(
    #     image: np.ndarray,
    #     text: str,
    #     box: np.ndarray,
    #     color: Tuple[int, int, int] = (0, 0, 255),
    #     font_size: float = 0.001,
    #     text_thickness: int = 2,
    # ) -> np.ndarray:
    #     x1, y1, x2, y2 = box.astype(int)

        

    #     (tw, th), _ = cv2.getTextSize(
    #         text=text,
    #         fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    #         fontScale=font_size,
    #         thickness=text_thickness,
    #     )

    #     th = int(th * 1.2)

    #     cv2.rectangle(image, (x1, y1), (x1 + tw, y1 - th), color, -1)

    #     return cv2.putText(
    #         image,
    #         text,
    #         (x1, y1),
    #         # font, #"/mnt/c/Users/Cain/Documents/github/prj_flax/flax/utility/fonts/fonts-japanese-gothic.ttf", #cv2.FONT_HERSHEY_SIMPLEX,
    #         font_size,
    #         (255, 255, 255),
    #         text_thickness,
    #         cv2.LINE_AA,
    #     )

    @staticmethod
    def draw_text_pil(
        image: np.ndarray,
        text: str,
        box: np.ndarray,
    ):
        x1, y1, x2, y2 = box.astype(int)
        image_pil = Image.fromarray(image)  # Convert OpenCV image to PIL image
        draw = ImageDraw.Draw(image_pil, "RGBA")
        draw.rectangle([(x1, y1-font_height), (x2, y1)], fill=(0, 0, 255, 64), outline=(0, 0, 255))
        draw.text((x1,y1-font_height), text, font=font, fill=(0,255,0,255))
        image_with_text  = np.array(image_pil)  # Convert PIL image back to OpenCV image
        # cv2.imwrite("debug.png", image_with_text)
        return image_with_text




def load_ocr(model = "manga_ocr"):
    if model == "manga_ocr":
        from manga_ocr import MangaOcr
        return MangaOcr()


def get_snippet(img, box):
    return Image.fromarray(img[int(box[1]):int(box[3]), int(box[0]):int(box[2])])


def main():
    data = get_images_from_path(DATAPATH,
        first_page=0,
        last_page=None,
        method_pdf="pdfium"
    )

    mocr = load_ocr()
    from time import time
    page_time = []
    for i, img in enumerate(data):
        print(f"Processing page {i}...")
        start_time = time()
        boxes, scores, class_names, elapse = layout_engine(img)

        display_text = []
        for (class_name, box, score) in zip(class_names, boxes, scores):
            if "text" in class_name :
                snippet = get_snippet(img, box)
                # run ocr
                text = mocr(snippet)
                
                display_text.append(f"{class_name}: {text}")
            else:
                display_text.append(class_name)

        page_time.append(time() - start_time)
        print(f"Page {i} processed in {page_time[-1]:.2f}s")
        # # run ocr
        # import pdb; pdb.set_trace()

        ploted_img = CustomVisLayout.draw_detections(img, boxes, scores, class_names)
        # draw text
        for box, text in zip(boxes, display_text):
            ploted_img = CustomVisLayout.draw_text_pil(ploted_img, text, box)
        
        if ploted_img is not None:
            basename = ".".join(os.path.basename(DATAPATH).split(".")[:-1])
            cv2.imwrite(os.path.join(OUTPATH, f"{basename}_{i}.png"), ploted_img)
        

    print(f"Average time per page: {sum(page_time)/len(page_time):.2f}s")

if __name__ == "__main__":
    main()