
import os
import sqlite3
from datetime import datetime
from flask import Flask, redirect, render_template, request
from ocr.ai_classifier import classify_text
from ocr.ocr_reader import extract_text

app = Flask(__name__)

# إعداد المجلدات
UPLOAD_FOLDER = "uploads"
DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "database.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# التأكد من وجود المجلدات الضرورية عند التشغيل
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html")

# رفع الصورة وتشغيل OCR
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return "لم يتم اختيار ملف"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # OCR & AI
        extracted_text = extract_text(filepath)
        data = classify_text(extracted_text)

        return render_template("review.html", data=data)

    return render_template("upload.html")

# حفظ البيانات
@app.route("/save", methods=["POST"])
def save():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO beneficiaries 
        (full_name, national_id, phone, gender, service_type, request_description, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.form["full_name"],
            request.form["national_id"],
            request.form["phone"],
            request.form["gender"],
            request.form["service_type"],
            request.form["request_description"],
            datetime.now().strftime("%Y-%m-%d") # إضافة تاريخ الحفظ
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # جلب البيانات
    cursor.execute("SELECT * FROM beneficiaries")
    data = cursor.fetchall()

    # إجمالي المستفيدين
    cursor.execute("SELECT COUNT(*) FROM beneficiaries")
    total = cursor.fetchone()[0]

    # طلبات اليوم (بشرط وجود عمود created_at في جدولك)
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM beneficiaries WHERE created_at = ?", (today_str,))
    today_count = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", data=data, total=total, today=today_count)

if __name__ == "__main__":
    app.run(debug=True)