from fastapi import FastAPI, UploadFile, File
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

@app.post("/upload")
@traceable
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    os.unlink(tmp_path)
    
    return {"message": "تم رفع الـ PDF بنجاح!"}

@app.post("/ask")
@traceable
async def ask_question(question: str):
    global vector_store
    
    if vector_store is None:
        return {"error": "ارفع PDF أولاً!"}
    
    docs = vector_store.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "أنت مساعد ذكي بتجاوب على الأسئلة بناءً على محتوى الـ PDF فقط"
            },
            {
                "role": "user",
                "content": f"السياق:\n{context}\n\nالسؤال: {question}"
            }
        ]
    )
    
    return {"answer": response.choices[0].message.content}