# 1. استخدام نسخة بايثون رسمية وخفيفة
FROM python:3.10-slim

# 2. تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# 3. تثبيت الأدوات النظامية المطلوبة للصوت والـ PDF
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. نسخ ملف الـ requirements وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. نسخ بقية ملفات المشروع (main.py, app.py, start.sh)
COPY . .

# 6. إعطاء صلاحية التشغيل لملف start.sh
RUN chmod +x start.sh

# 7. تشغيل السكربت الذي يفتح FastAPI و Streamlit معاً
CMD ["./start.sh"]