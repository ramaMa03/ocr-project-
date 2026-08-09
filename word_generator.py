
import os
from copy import deepcopy
from datetime import datetime

from docx import Document


TEMPLATE_PATH = "word_template/archive_template.docx"
OUTPUT_FOLDER = "generated_files"


def generate_word(data):

    # إنشاء مجلد الحفظ إذا لم يكن موجوداً
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # فتح النموذج
    doc = Document(TEMPLATE_PATH)

    # أول جدول في الملف
    table = doc.tables[0]

    # إنشاء صف جديد
    new_row = table.add_row()

    # نسخ تنسيق آخر صف
    last_row = table.rows[-2]

    for i in range(len(last_row.cells)):
        new_row.cells[i]._tc.clear_content()
        new_row.cells[i]._tc.get_or_add_tcPr()

        new_row.cells[i]._tc.append(
            deepcopy(last_row.cells[i]._tc.tcPr)
            if last_row.cells[i]._tc.tcPr
            else deepcopy(new_row.cells[i]._tc.get_or_add_tcPr())
        )

    # رقم السجل
    row_number = len(table.rows) - 1

    # تعبئة البيانات
    new_row.cells[0].text = str(row_number)

    new_row.cells[1].text = data.get(
        "letter_number",
        ""
    )

    new_row.cells[2].text = data.get(
        "letter_date",
        datetime.now().strftime("%Y-%m-%d")
    )

    new_row.cells[3].text = data.get(
        "organization",
        ""
    )

    new_row.cells[4].text = data.get(
        "full_name",
        ""
    )
        # اسم الملف الجديد
    file_name = f"سجل_الأرشفة_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    output_path = os.path.join(
        OUTPUT_FOLDER,
        file_name
    )

    # حفظ الملف
    doc.save(output_path)

    print(f"تم إنشاء ملف Word: {output_path}")

    return output_path


if __name__ == "__main__":

    sample_data = {

        "full_name": "محمد أحمد",

        "organization": "مركز التنمية الاجتماعية",

        "letter_number": "12345",

        "letter_date": "2026-07-01"

    }

    generate_word(sample_data)
    