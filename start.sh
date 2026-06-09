#!/bin/bash
# 1. تشغيل الـ Backend (FastAPI) في الخلفية على بورت 8000
uvicorn main:app --host 0.00.00 --port 8000 &

# 2. تشغيل الـ Frontend (Streamlit) على البورت الافتراضي لـ Hugging Face (7860)
streamlit run app.py --server.port 7860 --server.address 0.0.0.0