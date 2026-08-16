
import sqlite3
from datetime import datetime


DATABASE = "database.db"


# ==================================
# إنشاء الاتصال
# ==================================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ==================================
# إنشاء جدول الأرشيف
# ==================================

def create_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            client_name TEXT NOT NULL,

            letter_number TEXT NOT NULL,

            date TEXT NOT NULL,

            organization TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    conn.close()


# ==================================
# إضافة سجل جديد
# ==================================

def insert_record(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO archive (

            client_name,
            letter_number,
            date,
            organization

        )

        VALUES (?, ?, ?, ?)
    """, (

        data.get("client_name", "").strip(),

        data.get("letter_number", "").strip(),

        data.get("date", "").strip(),

        data.get("organization", "").strip()

    ))

    conn.commit()

    record_id = cursor.lastrowid

    conn.close()

    return record_id


# ==================================
# جلب جميع السجلات
# ==================================

def get_records():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM archive
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================
# جلب سجل واحد
# ==================================

def get_record(record_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM archive
        WHERE id = ?
    """, (record_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================
# تعديل سجل
# ==================================

def update_record(record_id, data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE archive

        SET

            client_name = ?,

            letter_number = ?,

            date = ?,

            organization = ?

        WHERE id = ?

    """, (

        data.get("client_name", "").strip(),

        data.get("letter_number", "").strip(),

        data.get("date", "").strip(),

        data.get("organization", "").strip(),

        record_id

    ))

    conn.commit()

    conn.close()


# ==================================
# حذف سجل
# ==================================

def delete_record(record_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM archive

        WHERE id = ?

    """, (record_id,))

    conn.commit()

    conn.close()


# ==================================
# البحث في الأرشيف
# ==================================

def search(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    keyword = f"%{keyword}%"


    cursor.execute("""
        SELECT *

        FROM archive

        WHERE

            client_name LIKE ?

            OR letter_number LIKE ?

            OR date LIKE ?

            OR organization LIKE ?

        ORDER BY id DESC

    """, (

        keyword,

        keyword,

        keyword,

        keyword

    ))


    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================
# عدد السجلات
# ==================================

def get_records_count():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)

        FROM archive
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# ==================================
# عدد سجلات اليوم
# ==================================

def get_today_count():

    conn = get_connection()

    cursor = conn.cursor()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cursor.execute("""
        SELECT COUNT(*)

        FROM archive

        WHERE date = ?

    """, (today,))

    count = cursor.fetchone()[0]

    conn.close()

    return count