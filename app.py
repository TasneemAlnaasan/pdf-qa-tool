import os
import gradio as gr
import tempfile
from fpdf import FPDF
# استيراد مكتبات معالجة اللغة العربية
import arabic_reshaper
from bidi.algorithm import get_display
from backend import process_pdf, generate_summary

import urllib.request

# تحميل الخط تلقائياً لو ما موجود
font_path = "Amiri-Regular.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve(
    "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
    font_path
    )

def create_pdf(summary_text):
    # 1. إنشاء كائن الـ PDF وتفعيل دعم الـ UTF-8
    pdf = FPDF()
    pdf.add_page()
    
    # 2. تسجيل وتفعيل الخط العربي (تأكد من وجود الملف في نفس المجلد)
    # إذا اخترت خطاً آخر، قم بتغيير الاسم والمسار هنا
    font_path = "Amiri-Regular.ttf" 
    
    if os.path.exists(font_path):
        pdf.add_font("ArabicFont", style="", fname=font_path, uni=True)
        pdf.set_font("ArabicFont", size=14)
    else:
        # خط احتياطي في حال عدم وجود الملف (لكن لن يعرض العربية بشكل صحيح)
        pdf.set_font("Helvetica", size=12)
        print("تحذير: لم يتم العثور على ملف الخط العربي Amiri-Regular.ttf")

    # 3. معالجة النص العربي ليظهر بشكل صحيح (تشبيك الحروف وعكس الاتجاه)
    reshaped_text = arabic_reshaper.reshape(summary_text) # تشبيك الحروف
    bidi_text = get_display(reshaped_text) # من اليمين إلى اليسار
    
    # محاذاة النص إلى اليمين 'R' لأنها لغة عربية
    pdf.multi_cell(0, 10, bidi_text, align='R')
    
    # 4. حفظ الملف المؤقت بشكل آمن لـ Gradio
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_path = tmp.name
    tmp.close() # إغلاق الملف لنتمكن من الكتابة فيه
    
    pdf.output(tmp_path)
    return tmp_path

def handle_pdf(file):
    if file is None:
        return "ارفع ملف أولاً!", None
        
    try:
        with open(file.name, "rb") as f:
            content = f.read()
        
        text = process_pdf(content)
        summary = generate_summary(text)
        pdf_path = create_pdf(summary)
        
        return summary, pdf_path
    except Exception as e:
        return f"حدث خطأ أثناء المعالجة: {str(e)}", None

# واجهة تطبيق Gradio
with gr.Blocks(title="PDF Summarizer") as demo:
    gr.Markdown("# 📄 PDF Summarizer")
    gr.Markdown("ارفع ملف PDF واحصل على ملخص فوري باللغة العربية!")
    
    file_input = gr.File(label="ارفع ملف PDF", file_types=[".pdf"])
    summarize_btn = gr.Button("📝 لخص الملف", variant="primary")
    summary_output = gr.Textbox(label="الملخص", interactive=False, lines=15)
    download_output = gr.File(label="⬇️ تنزيل الملخص كـ PDF")
    
    summarize_btn.click(
        fn=handle_pdf,
        inputs=[file_input],
        outputs=[summary_output, download_output]
    )

demo.launch()