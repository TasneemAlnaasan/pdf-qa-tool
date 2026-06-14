import streamlit as st
from groq import Groq
import os
import io
import json
from gtts import gTTS
import pypdf
import time 

st.set_page_config(page_title="المساعد الدراسي الذكي", page_icon="📚", layout="wide")
st.title("📚 المساعد الدراسي الذكي للطلاب")

# 1. جلب المفتاح من البيئة
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    st.error("❌ مفتاح GROQ_API_KEY غير معرف في الـ Secrets الخاصة بـ Hugging Face.")
    st.stop()

# تعريف عميل جروك
client = Groq(api_key=GROQ_KEY)

# استخدام الموديل الأحدث والمدعوم حالياً
SELECTED_MODEL = "llama-3.3-70b-versatile" 

# 2. زر رفع الملف
uploaded_file = st.file_uploader("ارفع ملف الدرس (PDF)", type="pdf")

if uploaded_file is not None:
    if 'file_processed' not in st.session_state:
        with st.spinner("جاري قراءة وتحليل كتابك بسرعة... ⚡"):
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
                full_text = ""
                max_pages = min(len(pdf_reader.pages), 10) 
                for page_num in range(max_pages):
                    page_text = pdf_reader.pages[page_num].extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                if not full_text.strip():
                    st.error("الملف فارغ أو عبارة عن صور فقط.")
                    st.stop()
                    
                st.session_state['full_text'] = full_text[:4000]
                st.session_state['file_processed'] = True
            except Exception as e:
                st.error(f"خطأ أثناء قراءة الملف: {str(e)}")
                st.stop()
                
        with st.spinner("جاري استدعاء الـ AI لتوليد الملخص والبطاقات الذكية... 🤖"):
            # توليد التلخيص
            try:
                sum_res = client.chat.completions.create(
                    model=SELECTED_MODEL,
                    messages=[
                        {"role": "system", "content": "لخص النص التالي باللغة العربية بأسلوب نقاط واضحة وموجزة."},
                        {"role": "user", "content": st.session_state['full_text']}
                    ]
                )
                st.session_state['summary'] = sum_res.choices[0].message.content
            except Exception as e:
                st.error(f"⚠️ فشل الاتصال بجروك لتوليد التلخيص: `{str(e)}`")
                st.session_state['summary'] = "تعذر توليد التلخيص بسبب خطأ في الـ API."
            
            # توليد الفلاش كاردز
            try:
                prompt = f"قم بإنشاء 3 بطاقات استذكار للمذاكرة بناءً على النص التالي. الإجابة بصيغة JSON فقط كقائمة تحتوي 'question' و 'answer'.\nالنص:\n{st.session_state['full_text']}"
                flash_res = client.chat.completions.create(
                    model=SELECTED_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                clean_json = flash_res.choices[0].message.content.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                st.session_state['flashcards'] = json.loads(clean_json)
            except Exception as e:
                st.session_state['flashcards'] = [
                    {"question": "لم يتم توليد البطاقات تلقائياً؟", "answer": f"بسبب خطأ الـ API التالي: {str(e)}"}
                ]

# 3. عرض الواجهة التفاعلية والتبويبات
if st.session_state.get('file_processed'):
    tab1, tab2, tab3 = st.tabs(["💬 اسأل الكتاب", "📝 ملخص الدرس", "🎴 بطاقات الاستذكار (Flashcards)"])
    
    with tab1:
        question = st.text_input("اكتب سؤالك عن المحاضرة بالعربي:")
        if st.button("ابحث عن الإجابة"):
            if question:
                with st.spinner("جاري صياغة الجواب من الكتاب..."):
                    try:
                        response = client.chat.completions.create(
                            model=SELECTED_MODEL,
                            messages=[
                                {"role": "system", "content": "أجب باللغة العربية بناءً على النص المرفق."},
                                {"role": "user", "content": f"الكتاب:\n{st.session_state['full_text']}\n\nالسؤال: {question}"}
                            ]
                        )
                        answer = response.choices[0].message.content
                        st.write("### 🤖 الإجابة:")
                        st.info(answer)
                    try:
                        time.sleep(1)    
                        tts = gTTS(text=answer, lang='ar', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp.read(), format="audio/mp3")
                    except Exception as e:
                        st.warning(f"تعذر توليد الصوت مؤقتا. لطفا أعد المحاولة مرة أخرى{str(e)}")

    with tab2:
        st.write("### 📝 ملخص سريع لأهم نقاط الدرس:")
        st.write(st.session_state.get('summary', 'لم يتم توليد ملخص.'))
        
    with tab3:
        st.write("### 🎴 اختبر نفسك مع بطاقات الاستذكار الذكية:")
        cards = st.session_state.get('flashcards', [])
        for i, card in enumerate(cards):
            with st.expander(f"📌 بطاقة رقم {i+1}: {card.get('question')}"):
                st.success(f"**الإجابة:** {card.get('answer')}")