FROM python:3.10-slim

WORKDIR /app

# تثبيت الأدوات الأساسية للنظام ومكتبة الكتم
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# تثبيت المكتبات بشكل تراتبي سليم مع إسكات التنبيهات بتركيب torchvision
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt torchvision

COPY . .

# إيقاف مراقب الملفات المزعج في ستريمليت نهائياً لعدم طباعة الأسطر الطويلة مجدداً
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0", "--server.fileWatcherType", "none"]