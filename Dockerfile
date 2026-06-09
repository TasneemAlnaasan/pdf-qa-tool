# 1. استخدام نسخة بايثون مستقرة
FROM python:3.10-slim

# 2. تحديد مجلد العمل
WORKDIR /app

# 3. نسخ ملف المكتبات أولاً
COPY requirements.txt .

# 4. تثبيت المكتبات وتأكيد ترقية pip لضمان تثبيت streamlit في المسار الصحيح
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. نسخ باقي ملفات المشروع لقراءة الكود
COPY . .

# 6. تحديث متغيرات النظام البيئية لضمان قراءة مكتبات بايثون
ENV PATH="/root/.local/bin:${PATH}"

# 7. تشغيل ستريمليت مباشرة من المسار التنفيذي لحل المشكلة نهائياً
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]