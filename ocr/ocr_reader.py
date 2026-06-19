
import pytesseract
from PIL import Image
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    try:
        # قراءة الصورة
        image = Image.open(image_path)
        
        # تحويل الصورة إلى RGB للتأكد من توافق الألوان
        image = image.convert('RGB')
        
        # استخراج النص مباشرة بدون معالجة OpenCV (المعالج الذاتي لـ Tesseract يعمل جيداً)
        # إعداد psm 6 مخصص لجداول الاستمارات
        text = pytesseract.image_to_string(image, lang="ara+eng", config="--psm 6")
        
        return text
    except Exception as e:
        print("خطأ في قراءة النص:", e)
        return ""