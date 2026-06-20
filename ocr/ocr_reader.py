import pytesseract
from PIL import Image
import os
import sys

# التعديل الذكي: نتحقق من نظام التشغيل
if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    # على السيرفر (Linux)، المحرك موجود تلقائياً
    pass

def extract_text(image_path):
    try:
        # التأكد من وجود الملف
        if not os.path.exists(image_path):
            print("خطأ: ملف الصورة غير موجود.")
            return ""

        # نفتح الصورة ونقلل حجمها لنوفر الذاكرة (Memory Management)
        with Image.open(image_path) as image:
            # تحويل للصيغة الرمادية لأنها أفضل للـ OCR وأخف
            image = image.convert('L')
            
            # تصغير الصورة لأقصى أبعاد (1000x1000) لضمان عدم انهيار السيرفر
            image.thumbnail((1000, 1000))
            
            # استخراج النص
            # استخدمنا 'ara+eng' كما طلبتِ، مع ضبط الإعدادات
            text = pytesseract.image_to_string(image, lang="ara+eng", config="--psm 6")
            
            return text
            
    except Exception as e:
        print("خطأ في قراءة النص:", e)
        return ""
