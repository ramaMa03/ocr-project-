
from docx import Document

import os
import re


# ==================================
# نموذج Word الجاهز
# ==================================

TEMPLATE_FILE = "word_template/archive_template.docx"


# ==================================
# مجلد ملفات Word الناتجة
# ==================================

OUTPUT_FOLDER = "static/word_files"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ==================================
# تحويل الأرقام العربية إلى إنجليزية
# ==================================

def normalize_digits(value):

    arabic_digits = "٠١٢٣٤٥٦٧٨٩"

    english_digits = "0123456789"

    translation = str.maketrans(
        arabic_digits,
        english_digits
    )

    return str(value).translate(
        translation
    )


# ==================================
# تحويل التاريخ الهجري إلى قيمة
# قابلة للترتيب
# ==================================

def hijri_sort_key(date_value):

    date_text = normalize_digits(
        date_value
    ).strip()

    numbers = re.findall(
        r"\d+",
        date_text
    )


    if len(numbers) >= 3:

        day = int(numbers[0])

        month = int(numbers[1])

        year = int(numbers[2])

        return (
            year,
            month,
            day
        )


    return (
        9999,
        99,
        99
    )


# ==================================
# ترتيب السجلات حسب التاريخ الهجري
# ==================================

def sort_records(records):

    return sorted(

        records,

        key=lambda record:
        hijri_sort_key(
            record["date"] or ""
        )

    )


# ==================================
# تقسيم السجلات
# كل 20 سجل
# ==================================

def split_records(records):

    groups = []

    for index in range(

        0,

        len(records),

        20

    ):

        groups.append(

            records[
                index:index + 20
            ]

        )

    return groups


# ==================================
# تجهيز ملف Word واحد
# ==================================

def create_group_word(

    records,

    group_number

):

    if not os.path.exists(
        TEMPLATE_FILE
    ):

        raise FileNotFoundError(

            f"لم يتم العثور على نموذج Word: {TEMPLATE_FILE}"

        )


    doc = Document(
        TEMPLATE_FILE
    )


    if not doc.tables:

        raise ValueError(

            "نموذج Word لا يحتوي على جدول."

        )


    table = doc.tables[0]


    # ==================================
    # التأكد من وجود 20 صفًا للبيانات
    # الصف الأول هو العناوين
    # ==================================

    while len(table.rows) < 21:

        table.add_row()


    # ==================================
    # مسح البيانات القديمة
    # ==================================

    for row_index in range(

        1,

        len(table.rows)

    ):

        for cell in table.rows[row_index].cells:

            cell.text = ""


    # ==================================
    # تعبئة السجلات
    # ==================================

    for index, record in enumerate(

        records,

        start=1

    ):

        row = table.rows[index]

        cells = row.cells


        if len(cells) < 5:

            raise ValueError(

                "نموذج Word لا يحتوي على الأعمدة الخمسة المطلوبة."

            )


        # العدد

        cells[0].text = str(index)


        # رقم الخطاب

        cells[1].text = (
            record["letter_number"] or ""
        )


        # التاريخ الهجري

        cells[2].text = (
            record["date"] or ""
        )


        # الجهة

        cells[3].text = (
            record["organization"] or ""
        )


        # اسم المواطن/ة

        cells[4].text = (
            record["client_name"] or ""
        )


    # ==================================
    # اسم الملف
    # ==================================

    filename = (
        f"archive_group_{group_number}.docx"
    )


    output_path = os.path.join(

        OUTPUT_FOLDER,

        filename

    )


    doc.save(
        output_path
    )


    return f"word_files/{filename}"


# ==================================
# إنشاء جميع ملفات Word
# ==================================

def create_word_files(records):

    sorted_records = sort_records(
        records
    )


    groups = split_records(
        sorted_records
    )


    generated_files = []

    for group_number, group in enumerate(

        groups,

        start=1

    ):

        word_file = create_group_word(

            group,

            group_number

        )


        generated_files.append({

            "records":
            group,

            "word_file":
            word_file

        })


    return generated_files


# ==================================
# الحصول على ملف Word الخاص بسجل
# ==================================

def get_word_for_record(

    records,

    record_id

):

    generated_files = create_word_files(
        records
    )


    for group in generated_files:

        for record in group["records"]:

            if record["id"] == record_id:

                return group["word_file"]


    return None