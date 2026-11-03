import os
import cv2
import numpy as np
import json

def parse_from_hf_dataset(category='validation'):
    from datasets import load_dataset
    out = f"iam/{category}"
    os.makedirs(out, exist_ok=True)
    ds = load_dataset("Teklia/IAM-line")
    ocr_label = []
    for idx, item in enumerate(ds[category]):
        item['image'].save(os.path.join(out, f"iam_{idx}.jpg"))
        ocr_label.append("|".join([f'iam_{idx}.jpg', item['text']]))
    
    with open(os.path.join(out, "ocr_label.txt"), "w") as f:
        f.write("\n".join(ocr_label))

if __name__ == "__main__":
    parse_from_hf_dataset()

    