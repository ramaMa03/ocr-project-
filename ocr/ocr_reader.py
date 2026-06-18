import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import re

# -----------------------------
# دالة قراءة النص من الصورة OCR
# -----------------------------
def extract_text(image_path):
    try:
        # قراءة الصورة
        img = cv2.imread(image_path)

        # تحويل إلى تدرج رمادي
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # إزالة التشويش
        gray = cv2.fastNlMeansDenoising(gray, h=30)

        # رفع التباين
        pil_img = Image.fromarray(gray)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(2)

        # تحويل إلى أبيض وأسود
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


# -----------------------------
# دالة استخراج الحقول من النص
# -----------------------------
def classify_text(text):

    data = {
        "full_name": "",
        "national_id": "",
        "phone": "",
        "gender": "",
        "service_type": "",
        "request_description": ""
    }

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # الاسم
        if any(word in line for word in ["الاسم", "اسم المستفيد", "اسم", "الاســم"]):
            data["full_name"] = re.sub(r"(الاسم|اسم المستفيد|اسم|:)", "", line).strip()

        # الهوية
        if any(word in line for word in ["الهوية", "رقم الهوية", "هويه", "هوية"]):
            data["national_id"] = re.sub(r"\D", "", line)

        # الجوال
        if any(word in line for word in ["الجوال", "رقم الجوال", "هاتف", "جوال"]):
            data["phone"] = re.sub(r"\D", "", line)

        # الجنس
        if "ذكر" in line:
            data["gender"] = "ذكر"
        if "أنثى" in line or "انثى" in line:
            data["gender"] = "أنثى"

    return data

