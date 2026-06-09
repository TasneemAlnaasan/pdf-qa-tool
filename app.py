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

# 1. جلب المفاتيح الصارمة من البيئة لـ Hugging Face
GROQ_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN_ENV = os.getenv("HF_TOKEN")

if not GROQ_KEY:
    st.error("❌ مفتاح GROQ_API_KEY غير معرف في الـ Secrets الخاصة بـ Hugging Face. يرجى إضافته وإعادة تشغيل التطبيق.")
    st.stop()

# 2. تحميل الموديل والـ Embeddings مرة واحدة في الذاكرة
@st.cache_resource
def load_llm_and_embeddings():
    client = Groq(api_key=GROQ_KEY)
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"token": HF_TOKEN_ENV} if HF_TOKEN_ENV else {}
    )
    return client, embeddings

client, embeddings = load_llm_and_embeddings()

# 3. زر رفع الملف (السطر الذي كان ناقصاً وتسبب بالخطأ)
uploaded_file = st.file_uploader("ارفع ملف الدرس (PDF)", type="pdf")

# 4. معالجة الملف وبناء قاعدة البيانات الذكية
if uploaded_file is not None:
    if 'file_processed' not in st.session_state:
        with st.spinner("جاري تحليل الكتاب وبناء المستودع الذكي..."):
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
            
        # توليد التلخيص والبطاقات فوراً عبر Groq Llama 3.3
        with st.spinner("جاري إنشاء التلخيص والـ Flashcards..."):
            # التلخيص
            sum_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "لخص النص التالي باللغة العربية بأسلوب نقاط واضحة وموجزة للطلاب."},
                    {"role": "user", "content": full_text}
                ]
            )
            st.session_state['summary'] = sum_res.choices[0].message.content
            
            # الفلاش كاردز
            prompt = f"بناءً على النص التالي، قم بإنشاء 4 بطاقات استذكار للمذاكرة. الإجابة بصيغة JSON فقط كقائمة تحتوي 'question' و 'answer'. لا تضع أي كلام خارج الـ JSON.\nالنص:\n{full_text}"
            flash_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            try:
                # تنظيف النص لضمان استخراجه كـ JSON نقي
                clean_json = flash_res.choices[0].message.content.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                st.session_state['flashcards'] = json.loads(clean_json)
            except:
                st.session_state['flashcards'] = [
                    {"question": "ما هي الفكرة العامة للملف؟", "answer": "راجع التلخيص في التبويب المجاور لملخص شامل."},
                    {"question": "كيف تستفيد من هذا الدرس؟", "answer": "عبر طرح أسئلة مباشرة في تبويب اسأل الكتاب."}
                ]

# 5. عرض الواجهة التفاعلية والتبويبات الثلاثة بعد رفع الملف
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
                            {"role": "system", "content": "أنت مساعد ذكي تجيب باللغة العربية الفصحى وبشكل مفصل ومبسط بناءً على السياق المرفق فقط وبأسلوب تعليمي."},
                            {"role": "user", "content": f"السياق:\n{context}\n\nالسؤال: {question}"}
                        ]
                    )
                    answer = response.choices[0].message.content
                    st.write("### 🤖 الإجابة:")
                    st.info(answer)
                    
                    # تحويل النص إلى صوت (Audio) مباشر
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