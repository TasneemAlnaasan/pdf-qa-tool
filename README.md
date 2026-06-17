---
title: PDF QA Tool
emoji: 📄
colorFrom: blue
colorTo: green
sdk: gradio
pinned: false
---

# 📄 PDF Summarizer

An AI-powered tool that summarizes any PDF instantly using LLaMA 3.

🔗 **Live Demo:** https://huggingface.co/spaces/Tsneemk/pdf-qa-tool 

## 🎯 What does it do?
- Upload any PDF file
- Get an instant summary in Arabic
- Download the summary as a PDF file

## 🛠️ Built With
- **Gradio** — User Interface
- **Groq + LLaMA 3** — AI Model

## 🚀 How to run
1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Add your API Key:
   - On Hugging Face: Add GROQ_API_KEY to Secrets
   - Locally: Create `.env` file and add GROQ_API_KEY=your_api_key_here
4. Run the app:
   python app.py

## 💡 Use Cases
- Students who want to summarize study material quickly
- Professionals who need to analyze long documents instantly