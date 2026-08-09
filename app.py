
import os
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request

from ocr.ai_classifier import classify_text
from ocr.ocr_reader import extract_text
from word_generator import generate_word

app = Flask(__name__)

# ==========================
# إعدادات المشروع
# ==========================

UPLOAD_FOLDER = "uploads"
DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "database.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# ==========================
# الصفحة الرئيسية
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# رفع الملف
# ==========================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or file.filename == "":
            return "لم يتم اختيار ملف"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        # قراءة النص
        extracted_text = extract_text(filepath)

        print("\n========== OCR TEXT ==========")
        print(extracted_text)
        print("================================\n")

        # استخراج البيانات
        data = classify_text(extracted_text)

        return render_template(
            "review.html",
            data=data
        )

    return render_template("upload.html")


# ==========================
# حفظ البيانات
# ==========================

@app.route("/save", methods=["POST"])
def save():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO beneficiaries
        (
            full_name,
            organization,
            letter_number,
            letter_date,
            request_description,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            request.form.get("full_name", ""),
            request.form.get("organization", ""),
            request.form.get("letter_number", ""),
            request.form.get("letter_date", ""),
            request.form.get("request_description", ""),
            datetime.now().strftime("%Y-%m-%d")
        )
    )

    conn.commit()
    conn.close()

    # إنشاء سجل الأرشفة في الوورد

    record = {
        "full_name": request.form.get("full_name", ""),
        "organization": request.form.get("organization", ""),
        "letter_number": request.form.get("letter_number", ""),
        "letter_date": request.form.get("letter_date", "")
    }

    generate_word(record)

    return redirect("/success")


# ==========================
# لوحة التحكم
# ==========================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM beneficiaries")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM beneficiaries")
    total = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM beneficiaries WHERE created_at=?",
        (today,)
    )

    today_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        today=today_count
    )


# ==========================
# صفحة النجاح
# ==========================

@app.route("/success")
def success():
    return render_template("success.html")


# ==========================
# تشغيل المشروع
# ==========================

if __name__ == "__main__":
    app.run(debug=True)