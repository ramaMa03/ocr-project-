FROM python:3.9-slim

# تحديث وتثبيت المحرك + ملف اللغة العربية
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-ara && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn app:app
