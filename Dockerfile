FROM python:3.9-slim

# تثبيت Tesseract مع دعم اللغة العربية
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-ara && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# الحل الجذري: زيادة وقت المهلة (Timeout) إلى 120 ثانية بدلاً من 30
# وزيادة عدد العمال (Workers) ليكونوا خفيفين على الذاكرة
CMD gunicorn --timeout 120 --workers 1 app:app
