from groq import Groq
import pypdf
import io
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SELECTED_MODEL = "llama-3.3-70b-versatile"

def process_pdf(file):
    pdf_reader = pypdf.PdfReader(io.BytesIO(file))
    full_text = ""
    max_pages = min(len(pdf_reader.pages), 10)
    for page_num in range(max_pages):
        page_text = pdf_reader.pages[page_num].extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text[:4000]

def generate_summary(text):
    response = client.chat.completions.create(
        model=SELECTED_MODEL,
        messages=[
            {"role": "system", "content": "لخص النص باللغة العربية بنقاط واضحة"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
