import gradio as gr
import tempfile
from fpdf import FPDF
from backend import process_pdf, generate_summary

def create_pdf(summary_text):
    pdf = FPDF()
        pdf.add_page()
            pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, summary_text)
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        pdf.output(tmp.name)
                            return tmp.name

                            def handle_pdf(file):
                                if file is None:
                                        return "ارفع ملف أولاً!", None
                                            with open(file.name, "rb") as f:
                                                    content = f.read()
                                                        text = process_pdf(content)
                                                            summary = generate_summary(text)
                                                                pdf_path = create_pdf(summary)
                                                                    return summary, pdf_path

                                                                    with gr.Blocks(title="PDF Summarizer") as demo:
                                                                        gr.Markdown("# 📄 PDF Summarizer")
                                                                            gr.Markdown("ارفع ملف PDF واحصل على ملخص فوري!")
                                                                                
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
