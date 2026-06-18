import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np

def extract_text(image_path):
    try:
        # قراءة الصورة باستخدام OpenCV
        img = cv2.imread(image_path)

        # تحويل إلى تدرج رمادي
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # إزالة التشويش
        gray = cv2.fastNlMeansDenoising(gray, h=30)

        # زيادة التباين
        pil_img = Image.fromarray(gray)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(2)

        # تحويل إلى أبيض وأسود (Threshold)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # حفظ نسخة مؤقتة
        temp_path = "temp_ocr.png"
        cv2.imwrite(temp_path, thresh)

        # إعدادات Tesseract
        custom_config = r"--oem 3 --psm 6 -l ara+eng"

        # قراءة النص
        text = pytesseract.image_to_string(temp_path, config=custom_config)

        return text

    except Exception as e:
        print("OCR Error:", e)
        return ""
