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

GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    st.error("❌ مفتاح GROQ_API_KEY غير معرف في الـ Secrets الخاصة بـ Hugging Face.")
    st.stop()

client = Groq(api_key=GROQ_KEY)
SELECTED_MODEL = "llama-3.3-70b-versatile"

# تهيئة المتغيرات في الـ session_state لمنع الأخطاء عند إعادة التشغيل
if 'file_processed' not in st.session_state:
    st.session_state['file_processed'] = False
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'flashcards' not in st.session_state:
    st.session_state['flashcards'] = None
if 'full_text' not in st.session_state:
    st.session_state['full_text'] = ""

uploaded_file = st.file_uploader("ارفع الملف(PDF)", type="pdf")

language = st.selectbox(
    "اختر لغة الإجابة والتلخيص والبطاقات:",
    ["العربية", "English", "Français", "Español"]
)

# زر لبدء المعالجة بعد اختيار اللغة بدقة
if uploaded_file is not None:
    if st.button("⚡ تحليل الملف وتوليد الملخص والبطاقات"):
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

        # توليد التلخيص بناءً على اللغة المختارة الحالية
        with st.spinner("جاري استدعاء الـ AI لتوليد الملخص... 🤖"):
            try:
                sum_res = client.chat.completions.create(
                    model=SELECTED_MODEL,
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant. You must write the summary completely in {language}. Use clear bullet points."},
                        {"role": "user", "content": f"Please summarize this text in {language}:\n\n{st.session_state['full_text']}"}
                    ]
                )
                st.session_state['summary'] = sum_res.choices[0].message.content
            except Exception as e:
                st.error(f"⚠️ فشل الاتصال بجروك لتوليد التلخيص: `{str(e)}`")
                st.session_state['summary'] = "تعذر توليد التلخيص بسبب خطأ في الـ API."

        # توليد بطاقات الاستذكار بناءً على اللغة المختارة الحالية
        with st.spinner("جاري توليد البطاقات الذكية... 🎴"):
            try:
                prompt = (
                    f"Create 3 flashcards based on the provided text. "
                    f"CRITICAL: The questions and answers must be entirely in {language}. "
                    f"Return ONLY a valid JSON list containing objects with 'question' and 'answer' keys. "
                    f"Do not include any intro or outro text. "
                    f"\nText:\n{st.session_state['full_text']}"
                )
                flash_res = client.chat.completions.create(
                    model=SELECTED_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                clean_json = flash_res.choices[0].message.content.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                st.session_state['flashcards'] = json.loads(clean_json)
            except Exception as e:
                st.session_state['flashcards'] = [
                    {"question": f"Error generating flashcards in {language}", "answer": f"Details: {str(e)}"}
                ]

# عرض النتائج في التبويبات إذا تمت المعالجة بنجاح
if st.session_state['file_processed']:
    tab1, tab2, tab3 = st.tabs(["💬 اسأل الكتاب", "📝 ملخص الدرس", "🎴 بطاقات الاستذكار (Flashcards)"])

    with tab1:
        question = st.text_input("اكتب سؤالك عن الملف هنا:")
        if st.button("ابحث عن الإجابة"):
            if question:
                with st.spinner("جاري صياغة الجواب من الملف..."):
                    try:
                        response = client.chat.completions.create(
                            model=SELECTED_MODEL,
                            messages=[
                                {"role": "system", "content": f"You are a helpful academic assistant. Answer the user's question based strictly on the text provided. You MUST answer entirely in {language}."},
                                {"role": "user", "content": f"Text:\n{st.session_state['full_text']}\n\nQuestion: {question}"}
                            ]
                        )
                        answer = response.choices[0].message.content
                        st.write("### 🤖 الإجابة:")
                        st.info(answer)
                        
                        # توليد الصوت بناءً على اللغة المحددة
                        try:
                            time.sleep(1)
                            lang_map = {"العربية": "ar", "English": "en", "Français": "fr", "Español": "es"}
                            lang_code = lang_map.get(language, "en")
                            
                            tts = gTTS(text=answer, lang=lang_code, slow=False)
                            fp = io.BytesIO()
                            tts.write_to_fp(fp)
                            fp.seek(0)
                            st.audio(fp.read(), format="audio/mp3")
                        except Exception as e:
                            st.warning(f"تعذر توليد الصوت مؤقتاً، جرب مرة ثانية: {str(e)}")
                    except Exception as e:
                        st.error(f"خطأ أثناء جلب الإجابة: {str(e)}")

    with tab2:
        st.write(f"### 📝 ملخص سريع لأهم نقاط الدرس ({language}):")
        if st.session_state['summary']:
            st.write(st.session_state['summary'])
        else:
            st.info("اضغط على زر التحليل في الأعلى لتوليد الملخص.")

    with tab3:
        st.write(f"### 🎴 اختبر نفسك مع بطاقات الاستذكار الذكية ({language}):")
        cards = st.session_state['flashcards']
        if cards:
            for i, card in enumerate(cards):
                with st.expander(f"📌 بطاقة رقم {i+1}: {card.get('question')}"):
                    st.success(f"**الإجابة:** {card.get('answer')}")
        else:
            st.info("اضغط على زر التحليل في الأعلى لتوليد بطاقات الاستذكار.")