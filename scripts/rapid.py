from rapidocr import RapidOCR

engine = RapidOCR()

# img_url = "https://github.com/RapidAI/RapidOCR/blob/main/python/tests/test_files/ch_en_num.jpg?raw=true"
img_url = '/mnt/c/Users/Cain/Documents/My Pictures/Screenshots/Screenshot 2026-01-05 144336.png'
result = engine(img_url)
print(result)

result.vis("vis_result.jpg")
