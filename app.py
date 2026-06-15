import gradio as gr
import io
import time
from gtts import gTTS
from backend import process_pdf, generate_summary, generate_flashcards, answer_question

def handle_pdf(file):
    if file is None:
        return "ارفع ملف أولاً!", "", ""
    with open(file.name, "rb") as f:
        content = f.read()
    text = process_pdf(content)
    summary = generate_summary(text)
    flashcards = generate_flashcards(text)
    return text, summary, flashcards

def handle_question(text, question):
    if not text:
        return "ارفع PDF أولاً!", None
    if not question:
        return "اكتب سؤال أولاً!", None
    answer = answer_question(text, question)
    try:
        time.sleep(1)
        tts = gTTS(text=answer, lang='ar', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio = fp.read()
    except:
        audio = None
    return answer, audio

with gr.Blocks(title="المساعد الدراسي الذكي") as demo:
    gr.Markdown("# 📚 المساعد الدراسي الذكي للطلاب")
    
    pdf_text = gr.State()
    
    with gr.Tab("📄 رفع الملف"):
        file_input = gr.File(label="ارفع ملف PDF", file_types=[".pdf"])
        upload_btn = gr.Button("تحليل الملف")
        status = gr.Textbox(label="الحالة", interactive=False)
    
    with gr.Tab("📝 الملخص"):
        summary_output = gr.Textbox(label="ملخص الدرس", interactive=False, lines=10)
    
    with gr.Tab("🎴 Flashcards"):
        flashcards_output = gr.Textbox(label="بطاقات الاستذكار", interactive=False, lines=10)
    
    with gr.Tab("💬 اسأل الكتاب"):
        question_input = gr.Textbox(label="اكتب سؤالك بالعربي")
        ask_btn = gr.Button("ابحث عن الإجابة")
        answer_output = gr.Textbox(label="الإجابة", interactive=False, lines=5)
        audio_output = gr.Audio(label="الإجابة الصوتية")
    
    upload_btn.click(
        fn=handle_pdf,
        inputs=[file_input],
        outputs=[pdf_text, summary_output, flashcards_output]
    )
    
    ask_btn.click(
        fn=handle_question,
        inputs=[pdf_text, question_input],
        outputs=[answer_output, audio_output]
    )

demo.launch()
