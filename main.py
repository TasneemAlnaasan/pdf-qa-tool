from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import tempfile
import io
import json
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# تفعيل الـ CORS لكي يتصل الـ Frontend بالـ Backend بدون مشاكل
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None
full_text = ""

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store, full_text
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    
    full_text = " ".join([doc.page_content for doc in documents])[:4000]
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    
    vector_store = FAISS.from_documents(chunks, embeddings)
    os.unlink(tmp_path)
    return {"message": "تم رفع الـ PDF بنجاح!"}

@app.post("/summarize")
async def get_summary():
    global full_text
    if not full_text: return {"error": "ارفع ملف أولاً"}
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "أنت مساعد أكاديمي. لخص النص التالي باللغة العربية بأسلوب نقاط واضحة وموجزة للطلاب."},
            {"role": "user", "content": full_text}
        ]
    )
    return {"summary": response.choices[0].message.content}

@app.post("/flashcards")
async def get_flashcards():
    global full_text
    if not full_text: return {"error": "ارفع ملف أولاً"}
    prompt = f"بناءً على النص التالي، قم بإنشاء 4 بطاقات استذكار للمذاكرة. الإجابة بصيغة JSON فقط كقائمة تحتوي 'question' و 'answer'. \nالنص:\n{full_text}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    try:
        cards = json.loads(response.choices[0].message.content)
        return {"flashcards": cards}
    except:
        return {"flashcards": [{"question": "اضغط مجدداً لتوليد البطاقات", "answer": "حدث خطأ في التنسيق"}]}

@app.post("/ask")
async def ask_question(question: str):
    global vector_store
    if vector_store is None: return {"error": "ارفع PDF أولاً!"}
    docs = vector_store.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "أنت مساعد ذكي تجيب باللغة العربية بناءً على الـ PDF فقط."},
            {"role": "user", "content": f"السياق:\n{context}\n\nالسؤال: {question}"}
        ]
    )
    return {"answer": response.choices[0].message.content}

@get_summary.get("/tts")
@app.get("/tts")
async def text_to_speech(text: str):
    tts = gTTS(text=text, lang='ar', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return StreamingResponse(fp, media_type="audio/mp3")