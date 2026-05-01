import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

st.set_page_config(page_title="PDF Q&A Tool", page_icon="📄")
st.title("📄 PDF Q&A Tool")
st.write("ارفع ملف PDF واسأل عنه أي سؤال!")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("جاري رفع الملف..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(documents)
        st.session_state.vector_store = FAISS.from_documents(chunks, embeddings)
        os.unlink(tmp_path)
        st.success("تم رفع الملف بنجاح! ✅")

question = st.text_input("اكتب سؤالك هنا")

if st.button("اسأل"):
    if question and st.session_state.vector_store:
        with st.spinner("جاري البحث عن الجواب..."):
            docs = st.session_state.vector_store.similarity_search(question, k=3)
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
            st.write("### الجواب:")
            st.write(response.choices[0].message.content)
    else:
        st.warning("ارفع PDF واكتب سؤال أولاً!")