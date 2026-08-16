from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file
)

import os
import uuid

from database import (
    create_database,
    insert_record,
    get_records,
    get_record,
    update_record,
    delete_record,
    get_records_count,
    get_today_count
)

from ocr import extract_text
from ai_parser import parse_text
from word_generator import create_word


# ==================================
# إنشاء التطبيق
# ==================================

app = Flask(__name__)

app.secret_key = "bayan_ocr"


# ==================================
# مجلد رفع الملفات
# ==================================

UPLOAD_FOLDER = "static/uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==================================
# إنشاء قاعدة البيانات
# ==================================

create_database()


# ==================================
# الصفحة الرئيسية
# ==================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================
# تسجيل الدخول
# ==================================

@app.route("/login")
def login():

    return render_template(
        "login.html"
    )


# ==================================
# لوحة التحكم
# ==================================

@app.route("/dashboard")
def dashboard():

    records = get_records()

    total_records = get_records_count()

    today = get_today_count()

    return render_template(
        "dashboard.html",

        total_clients=total_records,

        archived=total_records,

        today=today,

        accuracy="99%",

        records=records
    )


# ==================================
# صفحة رفع النماذج
# ==================================

@app.route("/upload")
def upload():

    return render_template(
        "upload.html"
    )


# ==================================
# الأرشيف
# ==================================

@app.route("/archive")
def archive():

    records = get_records()

    return render_template(
        "archive.html",

        records=records
    )


# ==================================
# جلب بيانات الأرشيف
# ==================================

@app.route("/archive-data")
def archive_data():

    records = get_records()

    data = []

    for record in records:

        data.append({

            "id": record["id"],

            "name":
            record["client_name"] or "",

            "letter_number":
            record["letter_number"] or "",

            "date":
            record["date"] or "",

            "department":
            record["organization"] or "",

            "count":
            record["id"]

        })

    return jsonify(data)


# ==================================
# صفحة النتائج
# ==================================

@app.route("/result")
def result():

    record_id = request.args.get("id")

    record = None

    if record_id:

        record = get_record(
            record_id
        )

    return render_template(
        "result.html",

        data=record
    )


# ==================================
# استقبال الصورة أو PDF وتشغيل OCR
# ==================================

@app.route(
    "/upload-image",
    methods=["POST"]
)
def upload_image():

    # ==================================
    # التأكد من وجود الملف
    # ==================================

    if "image" not in request.files:

        return jsonify({

            "success": False,

            "message":
            "الرجاء اختيار صورة أو ملف PDF"

        }), 400


    file = request.files["image"]


    # ==================================
    # التأكد من اختيار ملف
    # ==================================

    if file.filename == "":

        return jsonify({

            "success": False,

            "message":
            "لم يتم اختيار أي ملف"

        }), 400


    # ==================================
    # معلومات الملف
    # ==================================

    original_filename = (
        file.filename or ""
    )

    print("=" * 60)

    print(
        "ORIGINAL FILENAME:",
        original_filename
    )

    print(
        "CONTENT TYPE:",
        file.content_type
    )

    print("=" * 60)


    # ==================================
    # قراءة بداية الملف
    # لمعرفة نوعه الحقيقي
    # ==================================

    file.seek(0)

    file_header = file.read(8)

    file.seek(0)


    # ==================================
    # استخراج الامتداد
    # ==================================

    extension = os.path.splitext(
        original_filename
    )[1].lower()


    # ==================================
    # اكتشاف PDF من محتوى الملف
    # ==================================

    if file_header.startswith(
        b"%PDF"
    ):

        extension = ".pdf"


    # ==================================
    # اكتشاف JPEG
    # ==================================

    elif file_header.startswith(
        b"\xff\xd8\xff"
    ):

        extension = ".jpg"


    # ==================================
    # اكتشاف PNG
    # ==================================

    elif file_header.startswith(
        b"\x89PNG"
    ):

        extension = ".png"


    # ==================================
    # أنواع الملفات المسموحة
    # ==================================

    allowed_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff",
        ".pdf"

    }


    # ==================================
    # التحقق من نوع الملف
    # ==================================

    if extension not in allowed_extensions:

        print("=" * 60)

        print(
            "UNSUPPORTED FILE"
        )

        print(
            "Filename:",
            original_filename
        )

        print(
            "Content-Type:",
            file.content_type
        )

        print(
            "Header:",
            file_header
        )

        print("=" * 60)

        return jsonify({

            "success": False,

            "message":
            "نوع الملف غير مدعوم."

        }), 400


    # ==================================
    # إنشاء اسم فريد للملف
    # ==================================

    filename = (
        str(uuid.uuid4())
        + extension
    )


    filepath = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )


    # ==================================
    # حفظ الملف
    # ==================================

    file.seek(0)

    file.save(
        filepath
    )


    # ==================================
    # التأكد من حفظ الملف
    # ==================================

    print("=" * 60)

    print(
        "SAVED FILE:",
        filepath
    )

    print(
        "FILE EXTENSION:",
        extension
    )

    print(
        "FILE EXISTS:",
        os.path.exists(
            filepath
        )
    )

    if os.path.exists(filepath):

        print(
            "FILE SIZE:",
            os.path.getsize(
                filepath
            )
        )

    print("=" * 60)


    # ==================================
    # OCR
    # ==================================

    try:

        extracted_text = extract_text(
            filepath
        )

    except Exception as e:

        print(
            "OCR ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "حدث خطأ أثناء قراءة الملف."

        }), 500


    # ==================================
    # عرض النص المستخرج في Terminal
    # ==================================

    print("=" * 60)

    print(
        "EXTRACTED TEXT:"
    )

    print(
        extracted_text
    )

    print("=" * 60)


    # ==================================
    # تحليل النص
    # ==================================

    try:

        data = parse_text(
            extracted_text
        )

    except Exception as e:

        print(
            "AI PARSER ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "حدث خطأ أثناء تحليل البيانات."

        }), 500


    # ==================================
    # عرض البيانات المستخرجة
    # ==================================

    print("=" * 60)

    print(
        "PARSED DATA:"
    )

    print(
        data
    )

    print("=" * 60)


    # ==================================
    # إرسال النتائج إلى نفس الصفحة
    # ==================================

    return jsonify({

        "success": True,

        "data": data,

        "image": filename,

        "extracted_text": extracted_text,

        "filename": original_filename

    })


# ==================================
# حفظ سجل الأرشيف
# ==================================

@app.route(
    "/save",
    methods=["POST"]
)
def save():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                "لم يتم استقبال البيانات."

            }), 400


        archive_data = {

            "client_name":
            data.get(
                "client_name",
                ""
            ).strip(),

            "letter_number":
            data.get(
                "letter_number",
                ""
            ).strip(),

            "date":
            data.get(
                "date",
                ""
            ).strip(),

            "organization":
            data.get(
                "organization",
                ""
            ).strip()

        }


        # ==================================
        # التحقق من البيانات
        # ==================================

        if not archive_data["client_name"]:

            return jsonify({

                "success": False,

                "message":
                "يرجى إدخال اسم المواطن."

            }), 400


        if not archive_data["letter_number"]:

            return jsonify({

                "success": False,

                "message":
                "يرجى إدخال رقم الخطاب."

            }), 400


        if not archive_data["date"]:

            return jsonify({

                "success": False,

                "message":
                "يرجى إدخال التاريخ."

            }), 400


        if not archive_data["organization"]:

            return jsonify({

                "success": False,

                "message":
                "يرجى إدخال الجهة."

            }), 400


        # ==================================
        # حفظ في قاعدة البيانات
        # ==================================

        record_id = insert_record(
            archive_data
        )


        # ==================================
        # إنشاء ملف Word
        # ==================================

        word_file = create_word(
            archive_data
        )


        return jsonify({

            "success": True,

            "message":
            "تم حفظ البيانات وأرشفتها بنجاح.",

            "id":
            record_id,

            "word_file":
            word_file

        })


    except Exception as e:

        print(
            "SAVE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "حدث خطأ أثناء حفظ البيانات."

        }), 500


# ==================================
# تعديل سجل
# ==================================

@app.route(
    "/update/<int:record_id>",
    methods=["POST"]
)
def update(record_id):

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                "لم يتم استقبال البيانات."

            }), 400


        archive_data = {

            "client_name":
            data.get(
                "client_name",
                ""
            ).strip(),

            "letter_number":
            data.get(
                "letter_number",
                ""
            ).strip(),

            "date":
            data.get(
                "date",
                ""
            ).strip(),

            "organization":
            data.get(
                "organization",
                ""
            ).strip()

        }


        update_record(
            record_id,
            archive_data
        )


        return jsonify({

            "success": True,

            "message":
            "تم تعديل السجل بنجاح."

        })


    except Exception as e:

        print(
            "UPDATE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "حدث خطأ أثناء تعديل السجل."

        }), 500


# ==================================
# حذف سجل
# ==================================

@app.route(
    "/delete/<int:record_id>",
    methods=["DELETE"]
)
def delete(record_id):

    try:

        record = get_record(
            record_id
        )

        if not record:

            return jsonify({

                "success": False,

                "message":
                "السجل غير موجود."

            }), 404


        delete_record(
            record_id
        )


        return jsonify({

            "success": True,

            "message":
            "تم حذف السجل بنجاح."

        })


    except Exception as e:

        print(
            "DELETE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
            "حدث خطأ أثناء حذف السجل."

        }), 500


# ==================================
# فتح ملف Word
# ==================================

@app.route(
    "/word/<int:record_id>"
)
def word(record_id):

    record = get_record(
        record_id
    )

    if not record:

        return (
            "السجل غير موجود",
            404
        )


    data = {

        "client_name":
        record["client_name"] or "",

        "letter_number":
        record["letter_number"] or "",

        "date":
        record["date"] or "",

        "organization":
        record["organization"] or ""

    }


    word_file = create_word(
        data
    )


    file_path = os.path.join(
        "static",
        word_file
    )


    if not os.path.exists(
        file_path
    ):

        return (
            "ملف Word غير موجود",
            404
        )


    return send_file(
        file_path,
        as_attachment=False
    )


# ==================================
# الإعدادات
# ==================================

@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


# ==================================
# تشغيل المشروع
# ==================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )