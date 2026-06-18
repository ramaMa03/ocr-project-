
import re

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

        if "الاسم" in line:
            data["full_name"] = line.replace("الاسم", "").replace(":", "").strip()

        elif "الهوية" in line:
            data["national_id"] = re.sub(r"\D", "", line)

        elif "الجوال" in line:
            data["phone"] = re.sub(r"\D", "", line)

        elif "ذكر" in line:
            data["gender"] = "ذكر"

        elif "أنثى" in line:
            data["gender"] = "أنثى"

    return data