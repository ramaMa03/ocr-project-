
import re


# ==================================
# تنظيف النص العام
# ==================================

def normalize_text(text):

    if not text:
        return ""

    # توحيد بعض علامات الترقيم
    text = text.replace("：", ":")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    return text.strip()


# ==================================
# تنظيف قيمة الحقل
# ==================================

def clean_value(value):

    if not value:
        return ""

    value = value.strip()

    # إزالة الرموز من البداية
    value = re.sub(
        r"^[\s:,\-–—_]+",
        "",
        value
    )

    # إزالة الرموز من النهاية
    value = re.sub(
        r"[\s:,\-–—_]+$",
        "",
        value
    )

    return value.strip()


# ==================================
# معرفة هل السطر يحتوي على عنوان حقل
# ==================================

def contains_label(line, labels):

    line_lower = line.lower()

    for label in labels:

        if label in line_lower:
            return label

    return None


# ==================================
# استخراج القيمة بعد العنوان
# ==================================

def get_value_after_label(line, label):

    if not line or not label:
        return ""

    # إزالة العنوان مرة واحدة فقط
    value = re.sub(
        re.escape(label),
        "",
        line,
        count=1,
        flags=re.IGNORECASE
    )

    # إزالة : أو - أو الرموز بين العنوان والقيمة
    value = re.sub(
        r"^[\s:,\-–—_]+",
        "",
        value
    )

    return clean_value(value)


# ==================================
# التحقق من أن السطر عنوان حقل آخر
# ==================================

def is_another_field(line):

    labels = [

        "اسم المواطن",
        "اسم المواطنة",
        "اسم المستفيد",
        "اسم العميل",
        "الاسم",

        "رقم الخطاب",
        "رقم خطاب",

        "التاريخ",
        "تاريخ",

        "الجهة",
        "جهة",

        "العدد",

        "الموضوع",
        "الطلب",

        "المشكلة",
        "الحالة",

        "نوع الخدمة",

        "رقم الهوية",
        "رقم الهوية الوطنية",

        "رقم الجوال",
        "رقم الهاتف"

    ]

    return contains_label(
        line,
        labels
    ) is not None


# ==================================
# الحصول على السطر التالي المفيد
# ==================================

def get_next_useful_line(lines, index):

    for next_index in range(
        index + 1,
        min(index + 4, len(lines))
    ):

        value = clean_value(
            lines[next_index]
        )

        if not value:
            continue

        # إذا وصلنا إلى حقل آخر نتوقف
        if is_another_field(value):
            return ""

        return value

    return ""


# ==================================
# استخراج الاسم
# ==================================

def extract_client_name(lines):

    labels = [

        "اسم المواطنة",
        "اسم المواطن",
        "اسم المستفيد",
        "اسم العميل",
        "الاسم"

    ]

    for i, line in enumerate(lines):

        label = contains_label(
            line,
            labels
        )

        if not label:
            continue


        # ==================================
        # القيمة الموجودة في نفس السطر
        # ==================================

        value = get_value_after_label(
            line,
            label
        )


        # ==================================
        # حالة OCR:
        # اسم المواطن ة: فهد عبد العزيز
        # ==================================

        value = re.sub(
            r"^[\s:：\-–—_]*[ةه]\s*[:：\-–—]?\s*",
            "",
            value
        ).strip()


        if value:

            # إذا كان بعد الاسم حقل آخر
            if not is_another_field(value):

                return clean_value(value)


        # ==================================
        # إذا كانت القيمة في السطر التالي
        # ==================================

        next_value = get_next_useful_line(
            lines,
            i
        )

        if next_value:

            return clean_value(
                next_value
            )


    return ""


# ==================================
# استخراج رقم الخطاب
# ==================================

def extract_letter_number(lines):

    labels = [

        "رقم الخطاب",
        "رقم خطاب"

    ]

    for i, line in enumerate(lines):

        label = contains_label(
            line,
            labels
        )

        if not label:
            continue


        value = get_value_after_label(
            line,
            label
        )


        if value:

            # إزالة المسافات الزائدة فقط
            value = re.sub(
                r"\s+",
                " ",
                value
            )

            return clean_value(
                value
            )


        next_value = get_next_useful_line(
            lines,
            i
        )

        if next_value:

            return clean_value(
                next_value
            )


    return ""


# ==================================
# استخراج التاريخ
# ==================================

def extract_date(lines):

    labels = [

        "التاريخ",
        "تاريخ"

    ]

    for i, line in enumerate(lines):

        label = contains_label(
            line,
            labels
        )

        if not label:
            continue


        value = get_value_after_label(
            line,
            label
        )


        if value:

            return clean_value(
                value
            )


        next_value = get_next_useful_line(
            lines,
            i
        )

        if next_value:

            return clean_value(
                next_value
            )


    return ""


# ==================================
# استخراج الجهة
# ==================================

def extract_organization(lines):

    labels = [

        "الجهة",
        "جهة"

    ]

    for i, line in enumerate(lines):

        label = contains_label(
            line,
            labels
        )

        if not label:
            continue


        value = get_value_after_label(
            line,
            label
        )


        if value:

            return clean_value(
                value
            )


        next_value = get_next_useful_line(
            lines,
            i
        )

        if next_value:

            return clean_value(
                next_value
            )


    return ""


# ==================================
# استخراج بيانات الأرشفة
# ==================================

def parse_text(text):

    data = {

        "client_name": "",

        "letter_number": "",

        "date": "",

        "organization": ""

    }


    if not text:

        return data


    # ==================================
    # تنظيف النص
    # ==================================

    text = normalize_text(
        text
    )


    # ==================================
    # تقسيم النص إلى أسطر
    # ==================================

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]


    if not lines:

        return data


    # ==================================
    # استخراج الحقول المطلوبة فقط
    # ==================================

    data["client_name"] = (
        extract_client_name(lines)
    )


    data["letter_number"] = (
        extract_letter_number(lines)
    )


    data["date"] = (
        extract_date(lines)
    )


    data["organization"] = (
        extract_organization(lines)
    )


    # ==================================
    # عرض النتيجة في Terminal
    # ==================================

    print("=" * 60)

    print("PARSED DATA")

    print("=" * 60)

    print(
        "اسم المواطن:",
        data["client_name"]
    )

    print(
        "رقم الخطاب:",
        data["letter_number"]
    )

    print(
        "التاريخ:",
        data["date"]
    )

    print(
        "الجهة:",
        data["organization"]
    )

    print("=" * 60)


    return data