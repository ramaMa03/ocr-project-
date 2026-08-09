
import re

def classify_text(text):
    # الحقول البرمجية الداخلية المربوطة بالفورم الحالي (بدون أي تعديل في الواجهة)
    data = {
        "full_name": "",
        "national_id": "",
        "phone": "",
        "gender": "ذكر", 
        "service_type": "دعم اجتماعي", 
        "request_description": ""
    }

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # 1. التعرف الذكي على الاسم (سواء كُتب: الاسم الكامل، الاسم، اسم المستفيد)
        if "الاسم الكامل" in line or "الاسم" in line:
            # يحذف الكلمة الدلالية والنقطتين أياً كانت ليأخذ الاسم الصافي فقط
            clean_name = re.sub(r"(الاسم الكامل|الاسم|:)", "", line).strip()
            data["full_name"] = clean_name

        # 2. التعرف الذكي على الهوية (سواء كُتب: رقم السجل المدني، الهوية، السجل المدني، رقم الهوية)
        elif "السجل المدني" in line or "الهوية" in line or "رقم السجل" in line:
            # استخراج الأرقام فقط بمرونة عالية
            id_match = re.search(r"\d+", line)
            if id_match:
                data["national_id"] = id_match.group()

        # 3. التعرف الذكي على رقم الهاتف (سواء كُتب: رقم الجوال المسجل، الجوال، الهاتف، رقم الجوال)
        elif "الجوال" in line or "الهاتف" in line:
            phone_match = re.search(r"\d+", line)
            if phone_match:
                data["phone"] = phone_match.group()

        # 4. التعرف الذكي على نوع الخدمة (سواء كُتب: نوع البرنامج، الخدمة، نوع الخدمة)
        elif "نوع البرنامج" in line or "البرنامج" in line or "نوع الخدمة" in line:
            clean_service = re.sub(r"(نوع البرنامج|البرنامج|نوع الخدمة|:)", "", line).strip()
            data["service_type"] = clean_service

        # 5. التعرف الذكي على وصف الطلب (سواء كُتب: حالة الطلب، تفاصيل الطلب، وصف الطلب)
        elif "حالة الطلب" in line or "وصف الطلب" in line:
            clean_desc = re.sub(r"(حالة الطلب الحالي|حالة الطلب|وصف الطلب|:)", "", line).strip()
            data["request_description"] = clean_desc

        # 6. تحديد الجنس تلقائياً بناءً على محتوى السطر
        if "ذكر" in line:
            data["gender"] = "ذكر"
        elif "أنثى" in line or "امراة" in line:
            data["gender"] = "أنثى"

    return data