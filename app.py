import streamlit as st
import requests

st.set_page_config(page_title="المساعد الدراسي الذكي", page_icon="📚", layout="wide")
st.title("📚 المساعد الدراسي الذكي للطلاب")

# نستخدم localhost لأن السيرفرين سيعملان على نفس الـ Space في Hugging Face
API_URL = "http://localhost:8000"

uploaded_file = st.file_uploader("ارفع ملف الدرس (PDF)", type="pdf")

if uploaded_file is not None:
    if 'file_processed' not in st.session_state:
        with st.spinner("جاري تحليل الكتاب وبناء المستودع الذكي..."):
            files = {"file": uploaded_file}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code == 200:
                st.session_state['file_processed'] = True
                st.success("تم رفع وتحليل الملف بنجاح! 🎉")
                
                with st.spinner("جاري إنشاء التلخيص والـ Flashcards..."):
                    sum_res = requests.post(f"{API_URL}/summarize")
                    flash_res = requests.post(f"{API_URL}/flashcards")
                    st.session_state['summary'] = sum_res.json().get("summary", "لا يوجد ملخص")
                    st.session_state['flashcards'] = flash_res.json().get("flashcards", [])

if 'file_processed' in st.session_state:
    tab1, tab2, tab3 = st.tabs(["💬 اسأل الكتاب", "📝 ملخص الدرس", "🎴 بطاقات الاستذكار (Flashcards)"])
    
    with tab1:
        question = st.text_input("اكتب سؤالك عن المحاضرة بالعربي:")
        if st.button("ابحث عن الإجابة"):
            if question:
                with st.spinner("جاري استخراج الجواب..."):
                    response = requests.post(f"{API_URL}/ask", params={"question": question})
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.write("### 🤖 الإجابة:")
                        st.info(answer)
                        
                        st.write("🎧 الإجابة الصوتية:")
                        audio_res = requests.get(f"{API_URL}/tts", params={"text": answer})
                        if audio_res.status_code == 200:
                            st.audio(audio_res.content, format="audio/mp3")

    with tab2:
        st.write("### 📝 ملخص سريع لأهم نقاط الدرس:")
        st.write(st.session_state.get('summary', 'لم يتم توليد ملخص بعد.'))
        
    with tab3:
        st.write("### 🎴 اختبر نفسك مع بطاقات الاستذكار الذكية:")
        cards = st.session_state.get('flashcards', [])
        for i, card in enumerate(cards):
            with st.expander(f"📌 بطاقة رقم {i+1}: {card.get('question')}"):
                st.success(f"**الإجابة:** {card.get('answer')}")