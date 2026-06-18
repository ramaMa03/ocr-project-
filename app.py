
import os
import sqlite3
from flask import Flask, redirect, render_template, request
from ocr.ai_classifier import classify_text
from ocr.ocr_reader import extract_text

# تصحيح اسم المتغير هنا بإضافة الشرطات السفلية
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# تأكد من وجود مجلد التخزين حتى لا يظهر خطأ أثناء حفظ الملفات
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html")


# رفع الصورة وتشغيل OCR
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # تصحيح المسافات البادئة (Indentation)
        file = request.files.get("file")

        if not file or file.filename == "":
            return "لم يتم اختيار ملف"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # OCR
        extracted_text = extract_text(filepath)

        # AI Classifier
        data = classify_text(extracted_text)

        return render_template("review.html", data=data)

    return render_template("upload.html")


# حفظ البيانات
@app.route("/save", methods=["POST"])
def save():
    full_name = request.form["full_name"]
    national_id = request.form["national_id"]
    phone = request.form["phone"]
    gender = request.form["gender"]
    service_type = request.form["service_type"]
    request_description = request.form["request_description"]

    # تأكد من أن مجلد database موجود قبل تشغيل الكود
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO beneficiaries 
    (full_name, national_id, phone, gender, service_type, request_description) 
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            full_name,
            national_id,
            phone,
            gender,
            service_type,
            request_description,
        ),
    )

    conn.commit()
    conn.close()

    return redirect("/success")


# صفحة النجاح
@app.route("/success")
def success():
    return render_template("success.html")


# لوحة التحكم
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM beneficiaries")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM beneficiaries")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html", data=data, total=total, today=total
    )


# تصحيح التحقق من تشغيل الملف مباشرة
if __name__ == "__main__":
    app.run(debug=True)