
import sqlite3

# إنشاء اتصال بقاعدة البيانات
conn = sqlite3.connect('database/database.db')

# إنشاء المؤشر
cursor = conn.cursor()

# إنشاء جدول المستفيدين
cursor.execute('''

CREATE TABLE IF NOT EXISTS beneficiaries (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    national_id TEXT NOT NULL,

    phone TEXT,

    gender TEXT,

    service_type TEXT,

    request_description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

''')

# حفظ التغييرات
conn.commit()

# إغلاق الاتصال
conn.close()

print("Database Created Successfully")