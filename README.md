
---
title: PDF Academic Assistant
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📚 المساعد الدراسي الذكي للطلاب

An AI-powered study assistant that helps students learn smarter.

🔗 **Live Demo:** https://huggingface.co/spaces/Tsneemk/study-buddy

## 🎯 What does it do?
- Upload any PDF study material
- Get an instant summary in your language
- Auto-generated Flashcards for studying
- Ask questions and get voice answers

## 🛠️ Built With
- **Streamlit** — User Interface
- **Groq + LLaMA 3** — AI Model
- **gTTS** — Text to Speech
- **Docker** — Deployment

## 🚀 How to run
1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Add your API Key:
   - On Hugging Face: Add GROQ_API_KEY to Secrets
   - Locally: Create `.env` file and add GROQ_API_KEY=your_api_key_here
4. Run the app:
   streamlit run app.py

## 💡 Use Cases
- Students studying for exams
- Anyone who wants to learn from PDFs faster