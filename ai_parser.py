
import re
import unicodedata


# ============================================================
# تنظيف النص
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "：": ":",
        "؛": ";",
        "،": ",",
        "–": "-",
        "—": "-",
        "ـ": "",
        "\u200f": "",
        "\u200e": "",
        "\ufeff": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# ============================================================
# تحويل الأرقام العربية إلى إنجليزية
# ============================================================

def normalize_digits(text):

    if not text:
        return ""

    table = str.maketrans(
        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
        "01234567890123456789"
    )

    return text.translate(table)


# ============================================================
# تنظيف قيمة
# ============================================================

def clean_value(value):

    if not value:
        return ""

    value = normalize_text(value)

    value = re.sub(
        r"^[\s:،,؛;\-–—_=|]+",
        "",
        value
    )

    value = re.sub(
        r"[\s:،,؛;\-–—_=|]+$",
        "",
        value
    )

    return value.strip()


# ============================================================
# عناوين الحقول
# ============================================================

FIELD_LABELS = {

    "name": [
        "الاسم الكامل",
        "اسم المواطن/ة",
        "اسم المواطن /ة",
        "اسم المواطنه",
        "اسم المواطنة",
        "اسم المواطن",
        "اسم المستفيد/ة",
        "اسم المستفيد",
        "اسم المستفيدة",
        "اسم العميل/ة",
        "اسم العميل",
        "اسم العميلة",
        "الاسم"
    ],

    "letter_number": [
        "رقم الخطاب",
        "رقم خطاب"
    ],

    "date": [
        "تاريخ الخطاب",
        "التاريخ",
        "تاريخ"
    ],

    "organization": [
        "اسم الجهة",
        "الجهة المرسلة",
        "الجهة المستفيدة",
        "الجهة",
        "جهة"
    ]
}


# ============================================================
# عناوين توقف استخراج الاسم
# ============================================================

STOP_LABELS = [
    "رقم السجل المدني",
    "رقم الهوية",
    "رقم الهوية الوطنية",
    "رقم الجوال",
    "رقم الهاتف",
    "العنوان",
    "الجنس",
    "الحالة الاجتماعية",
    "المدينة",
    "المنطقة",
    "تاريخ الميلاد",
    "الجنسية",
    "رقم الخطاب",
    "رقم خطاب",
    "التاريخ",
    "تاريخ الخطاب",
    "الجهة",
    "اسم الجهة",
    "الموضوع",
    "نوع الخدمة",
    "الطلب",
    "الحالة"
]


# ============================================================
# هل السطر عنوان حقل؟
# ============================================================

def contains_label(line, labels):

    if not line:
        return False

    normalized = normalize_text(line)

    for label in labels:

        if label in normalized:
            return True

    return False


# ============================================================
# هل السطر حقل آخر؟
# ============================================================

def is_field_line(line):

    if not line:
        return False

    for field in FIELD_LABELS.values():

        if contains_label(
            line,
            field
        ):
            return True

    for label in STOP_LABELS:

        if label in line:
            return True

    return False


# ============================================================
# استخراج ما بعد العنوان
# ============================================================

def get_after_label(line, label):

    if not line or not label:
        return ""

    index = line.find(label)

    if index == -1:
        return ""

    value = line[
        index + len(label):
    ]

    value = re.sub(
        r"^[\s:：\-–—_/]+",
        "",
        value
    )

    return clean_value(value)


# ============================================================
# هل النص اسم منطقي؟
# ============================================================

def valid_name(value):

    if not value:
        return False

    value = clean_value(value)

    if len(value) < 3:
        return False

    # الاسم لا ينبغي أن يحتوي أرقامًا
    if re.search(r"\d", value):
        return False

    # يجب أن يحتوي حروفًا
    if not re.search(
        r"[A-Za-z\u0600-\u06FF]",
        value
    ):
        return False

    return True


# ============================================================
# استخراج الاسم
# ============================================================

def extract_client_name(lines):

    for i, line in enumerate(lines):

        if not line:
            continue

        # ----------------------------------------------------
        # البحث عن "الاسم الكامل" أولًا
        # ----------------------------------------------------

        label = None

        for candidate in FIELD_LABELS["name"]:

            if candidate in line:
                label = candidate
                break

        if not label:
            continue

        # ----------------------------------------------------
        # القيمة في نفس السطر
        # ----------------------------------------------------

        value = get_after_label(
            line,
            label
        )

        if value:

            # إزالة كلمات غير مرغوبة
            value = re.sub(
                r"^[\s:：\-–—_/]+",
                "",
                value
            )

            value = clean_value(value)

        # ----------------------------------------------------
        # إذا لم توجد قيمة في نفس السطر
        # ----------------------------------------------------

        collected = []

        if value and valid_name(value):

            collected.append(value)

        # ----------------------------------------------------
        # نقرأ الأسطر التالية لاستكمال الاسم
        # ----------------------------------------------------

        for j in range(
            i + 1,
            min(i + 4, len(lines))
        ):

            next_line = clean_value(
                lines[j]
            )

            if not next_line:
                continue

            # توقف عند بداية حقل جديد
            if is_field_line(next_line):
                break

            # لا نريد أرقام داخل الاسم
            if re.search(
                r"\d",
                next_line
            ):
                break

            # يجب أن يحتوي على حروف
            if not re.search(
                r"[A-Za-z\u0600-\u06FF]",
                next_line
            ):
                continue

            collected.append(next_line)

            # الاسم عادة لا يحتاج أكثر من سطرين
            if len(" ".join(collected)) > 100:
                break

        # ----------------------------------------------------
        # دمج أجزاء الاسم
        # ----------------------------------------------------

        if collected:

            result = " ".join(
                collected
            )

            result = clean_value(
                result
            )

            if valid_name(result):

                # إزالة بقايا "الكامل"
                result = re.sub(
                    r"^الكامل\s*[:：\-]?\s*",
                    "",
                    result
                )

                return result.strip()

    return ""


# ============================================================
# استخراج رقم الخطاب
# ============================================================

def extract_letter_number(lines):

    for i, line in enumerate(lines):

        label = None

        for candidate in FIELD_LABELS["letter_number"]:

            if candidate in line:
                label = candidate
                break

        if not label:
            continue

        value = get_after_label(
            line,
            label
        )

        # إذا كان الرقم في نفس السطر
        if value:

            value = normalize_digits(
                value
            )

            # الاحتفاظ بالأرقام والحروف والرموز المعتادة
            value = re.sub(
                r"[^\w\-/.]",
                "",
                value,
                flags=re.UNICODE
            )

            if re.search(
                r"\d",
                value
            ):
                return value

        # الرقم في السطر التالي
        if i + 1 < len(lines):

            next_line = clean_value(
                lines[i + 1]
            )

            if next_line:

                next_line = normalize_digits(
                    next_line
                )

                next_line = re.sub(
                    r"[^\w\-/.]",
                    "",
                    next_line,
                    flags=re.UNICODE
                )

                if re.search(
                    r"\d",
                    next_line
                ):
                    return next_line

    return ""


# ============================================================
# استخراج التاريخ
# ============================================================

def normalize_date(value):

    if not value:
        return ""

    value = normalize_digits(
        value
    )

    value = value.replace(
        "/",
        "-"
    )

    value = value.replace(
        ".",
        "-"
    )

    value = re.sub(
        r"\s+",
        "",
        value
    )

    # DD-MM-YYYY
    match = re.search(
        r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b",
        value
    )

    if match:

        day = int(
            match.group(1)
        )

        month = int(
            match.group(2)
        )

        year = int(
            match.group(3)
        )

        if (
            1 <= day <= 31
            and
            1 <= month <= 12
        ):

            return (
                f"{day:02d}-"
                f"{month:02d}-"
                f"{year}"
            )

    # YYYY-MM-DD
    match = re.search(
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
        value
    )

    if match:

        year = int(
            match.group(1)
        )

        month = int(
            match.group(2)
        )

        day = int(
            match.group(3)
        )

        if (
            1 <= day <= 31
            and
            1 <= month <= 12
        ):

            return (
                f"{day:02d}-"
                f"{month:02d}-"
                f"{year}"
            )

    return ""


def extract_date(lines):

    # أولًا ابحث عن التاريخ بجانب عنوانه
    for i, line in enumerate(lines):

        for label in FIELD_LABELS["date"]:

            if label not in line:
                continue

            value = get_after_label(
                line,
                label
            )

            result = normalize_date(
                value
            )

            if result:
                return result

            if i + 1 < len(lines):

                result = normalize_date(
                    lines[i + 1]
                )

                if result:
                    return result

    # محاولة أخيرة: أي تاريخ في النص
    for line in lines:

        result = normalize_date(
            line
        )

        if result:
            return result

    return ""


# ============================================================
# استخراج الجهة
# ============================================================

def extract_organization(lines):

    for i, line in enumerate(lines):

        label = None

        for candidate in FIELD_LABELS["organization"]:

            if candidate in line:
                label = candidate
                break

        if not label:
            continue

        value = get_after_label(
            line,
            label
        )

        if value:

            # إزالة رموز البداية
            value = clean_value(
                value
            )

            if len(value) >= 3:
                return value

        # الجهة في السطر التالي
        if i + 1 < len(lines):

            next_line = clean_value(
                lines[i + 1]
            )

            if (
                next_line
                and
                not is_field_line(next_line)
                and
                len(next_line) >= 3
            ):

                return next_line

    return ""


# ============================================================
# الدالة الرئيسية
# ============================================================

def parse_text(text):

    data = {
        "client_name": "",
        "letter_number": "",
        "date": "",
        "organization": ""
    }

    if not text:
        return data

    text = normalize_text(
        text
    )

    lines = [
        clean_value(line)
        for line in text.splitlines()
        if clean_value(line)
    ]

    if not lines:
        return data

    # --------------------------------------------------------
    # استخراج البيانات
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # عرض النتيجة
    # --------------------------------------------------------

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