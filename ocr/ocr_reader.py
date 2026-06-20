import pytesseract
from PIL import Image
import os
import sys

# التعديل الذكي: نتحقق من نظام التشغيل
if sys.platform == "win32":
    # إذا كنتِ على جهازك (ويندوز)، استخدمي هذا المسار
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    # إذا كنتِ على السيرفر (Linux/Render)، لا نحتاج لتحديد مسار، 
    # سيقوم النظام بالبحث عن المحرك تلقائياً في المسار العام
    pass

def extract_text(image_path):
    try:
        # التأكد من وجود الملف قبل المعالجة
        if not os.path.exists(image_path):
            print("خطأ: ملف الصورة غير موجود.")
            return ""

        image = Image.open(image_path)
        image = image.convert('RGB')
        
        # استخراج النص
        text = pytesseract.image_to_string(image, lang="ara+eng", config="--psm 6")
        
        return text
    except Exception as e:
        print("خطأ في قراءة النص:", e)
        return ""
