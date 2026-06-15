from groq import Groq
import pypdf
import io
import json
import os
from dotenv import load_dotenv

load_dotenv()

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

def generate_flashcards(text):
    prompt = f"أنشئ 3 بطاقات استذكار. JSON فقط كقائمة تحتوي 'question' و 'answer'.\nالنص:\n{text}"
    response = client.chat.completions.create(
        model=SELECTED_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    try:
        clean_json = response.choices[0].message.content.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
        cards = json.loads(clean_json)
        result = ""
        for i, card in enumerate(cards):
            result += f"بطاقة {i+1}:\nسؤال: {card.get('question')}\nجواب: {card.get('answer')}\n\n"
        return result
    except:
        return "تعذر توليد البطاقات، جرب مرة ثانية"


def answer_question(text, question):
    response = client.chat.completions.create(
        model=SELECTED_MODEL,
        messages=[
            {"role": "system", "content": "أجب باللغة العربية بناءً على النص المرفق فقط"},
            {"role": "user", "content": f"الكتاب:\n{text}\n\nالسؤال: {question}"}
        ]
    )
    return response.choices[0].message.content
