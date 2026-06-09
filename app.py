import streamlit as st
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

st.set_page_config(page_title="المساعد الدراسي الذكي", page_icon="📚", layout="wide")
st.title("📚 المساعد الدراسي الذكي للطلاب")

# تعريف الموديل والذكاء الاصطناعي مباشرة في الواجهة
@st.cache_resource
def load_llm_and_embeddings():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return client, embeddings

try:
    client, embeddings = load_llm_and_embeddings()
except Exception as e:
    st.error("تأكد من إضافة مفتاح GROQ_API_KEY في إعدادات الـ Secrets")

uploaded_file = st.file_uploader("ارفع ملف الدرس (PDF)", type="pdf")

if uploaded_file is not None:
    if 'file_processed' not in st.session_state:
        with st.spinner("جاري تحليل الكتاب وبناء المستودع الذكي..."):
            # حفظ الملف مؤقتاً وقراءته
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            full_text = " ".join([doc.page_content for doc in documents])[:4000]
            st.session_state['full_text'] = full_text
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(documents)
            
            st.session_state['vector_store'] = FAISS.from_documents(chunks, embeddings)
            os.unlink(tmp_path)
            st.session_state['file_processed'] = True
            
        # توليد التلخيص والبطاقات فوراً بدون أخطاء بورتات
        with st.spinner("جاري إنشاء التلخيص والـ Flashcards..."):
            # 1. التلخيص
            sum_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "لخص النص التالي باللغة العربية بأسلوب نقاط واضحة وموجزة للطلاب."},
                    {"role": "user", "content": full_text}
                ]
            )
            st.session_state['summary'] = sum_res.choices[0].message.content
            
            # 2. الفلاش كاردز
            prompt = f"بناءً على النص التالي، قم بإنشاء 4 بطاقات استذكار للمذاكرة. الإجابة بصيغة JSON فقط كقائمة تحتوي 'question' و 'answer'. \nالنص:\n{full_text}"
            flash_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            try:
                st.session_state['flashcards'] = json.loads(flash_res.choices[0].message.content)
            except:
                st.session_state['flashcards'] = [{"question": "اضغط مجدداً لتوليد البطاقات", "answer": "حدث خطأ في التنسيق"}]

if 'file_processed' in st.session_state:
    tab1, tab2, tab3 = st.tabs(["💬 اسأل الكتاب", "📝 ملخص الدرس", "🎴 بطاقات الاستذكار (Flashcards)"])
    
    with tab1:
        question = st.text_input("اكتب سؤالك عن المحاضرة بالعربي:")
        if st.button("ابحث عن الإجابة"):
            if question:
                with st.spinner("جاري استخراج الجواب..."):
                    docs = st.session_state['vector_store'].similarity_search(question, k=3)
                    context = "\n".join([doc.page_content for doc in docs])
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "أنت مساعد ذكي تجيب باللغة العربية بناءً على الـ PDF فقط."},
                            {"role": "user", "content": f"السياق:\n{context}\n\nالسؤال: {question}"}
                        ]
                    )
                    answer = response.choices[0].message.content
                    st.write("### 🤖 الإجابة:")
                    st.info(answer)
                    
                    # تحويل النص إلى صوت مباشرة وعرضه في واجهة Streamlit
                    tts = gTTS(text=answer, lang='ar', slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp.read(), format="audio/mp3")

    with tab2:
        st.write("### 📝 ملخص سريع لأهم نقاط الدرس:")
        st.write(st.session_state.get('summary', 'لم يتم توليد ملخص بعد.'))
        
    with tab3:
        st.write("### 🎴 اختبر نفسك مع بطاقات الاستذكار الذكية:")
        cards = st.session_state.get('flashcards', [])
        for i, card in enumerate(cards):
            with st.expander(f"📌 بطاقة رقم {i+1}: {card.get('question')}"):
                st.success(f"**الإجابة:** {card.get('answer')}")