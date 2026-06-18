import easyocr
import re

# -----------------------------
# دالة قراءة النص من الصورة OCR
# -----------------------------
def extract_text(image_path):
    try:
        reader = easyocr.Reader(['ar', 'en'])
        result = reader.readtext(image_path, detail=0)
        text = "\n".join(result)
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
