FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل ستريمليت مباشرة بدون الحاجة لملف start.sh واختفاء خطأ الـ exec format للأبد
CMD ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]