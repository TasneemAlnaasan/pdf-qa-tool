
# 📄 PDF Q&A Tool
An AI-powered tool that lets you upload any PDF and ask questions about its content using LLaMA 3.

## 🎯 What does it do?
- Upload any PDF file
- Ask questions in Arabic or English
- Get instant answers based on the PDF content

## 🛠️ Built With
- **FastAPI** — Backend API
- **Streamlit** — User Interface
- **Groq + LLaMA 3** — AI Model
- **LangChain** — PDF processing
- **FAISS** — Vector search

## 🚀 How to run
1. Clone the repository
2. Install dependencies:
pip install -r requirements.txt
3. Create `.env` file and add your Groq API Key:
GROQ_API_KEY=your_api_key_here
4. Run FastAPI:
uvicorn main:app --reload
5. Run Streamlit:
streamlit run app.py

## 💡 Use Cases
- Students can upload study material and ask questions
- Professionals can analyze long documents instantly
- Anyone who wants to extract information from PDFs quickly