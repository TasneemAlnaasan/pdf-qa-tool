import streamlit as st
import requests

st.set_page_config(page_title="PDF Q&A Tool", page_icon="📄")

st.title("📄 PDF Q&A Tool")
st.write("ارفع ملف PDF واسأل عنه أي سؤال!")

uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("جاري رفع الملف..."):
        files = {"file": uploaded_file}
        response = requests.post("http://localhost:8000/upload", files=files)
        if response.status_code == 200:
            st.success("تم رفع الملف بنجاح! ✅")

question = st.text_input("اكتب سؤالك هنا")

if st.button("اسأل"):
    if question:
        with st.spinner("جاري البحث عن الجواب..."):
            response = requests.post(
                "http://localhost:8000/ask",
                params={"question": question}
            )
            if response.status_code == 200:
                st.write("### الجواب:")
                st.write(response.json()["answer"])
    else:
        st.warning("اكتب سؤال أولاً!")