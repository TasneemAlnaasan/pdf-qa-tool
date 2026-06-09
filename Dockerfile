FROM python:3.10

WORKDIR /app

# نسخ ملف المكتبات أولاً لتسريع البناء
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية الملفات
COPY . .

# إعطاء صلاحية التشغيل
RUN chmod +x start.sh

# نقطة الانطلاق
CMD ["./start.sh"]