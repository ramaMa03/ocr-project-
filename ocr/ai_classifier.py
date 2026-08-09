
import re


def classify_text(text):

    data = {
        "full_name": "",
        "organization": "",
        "letter_number": "",
        "letter_date": "",
        "request_description": ""
    }

    # ==========================
    # اسم المواطن / المستفيد
    # ==========================

    patterns = [
        r"اسم المواطن\s*[:：]?\s*(.+)",
        r"اسم المواطنة\s*[:：]?\s*(.+)",
        r"اسم المستفيد\s*[:：]?\s*(.+)",
        r"الاسم\s*[:：]?\s*(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            data["full_name"] = match.group(1).strip()
            break

    # ==========================
    # الجهة
    # ==========================

    match = re.search(r"الجهة\s*[:：]?\s*(.+)", text)

    if match:
        data["organization"] = match.group(1).strip()

    # ==========================
    # رقم الخطاب
    # ==========================

    match = re.search(r"رقم الخطاب\s*[:：]?\s*([^\n]+)", text)

    if match:
        data["letter_number"] = match.group(1).strip()

    # ==========================
    # التاريخ
    # ==========================

    match = re.search(r"التاريخ\s*[:：]?\s*([0-9/\-]+)", text)

    if match:
        data["letter_date"] = match.group(1).strip()

    # ==========================
    # وصف الطلب
    # ==========================

    lines = text.split("\n")

    description = []

    start = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "اسم المواطن" in line or "اسم المستفيد" in line:
            start = True
            continue

        if start:
            description.append(line)

    data["request_description"] = " ".join(description)

    return data