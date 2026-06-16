import gradio as gr
from backend import process_pdf, generate_summary

def handle_pdf(file):
    if file is None:
        return "ارفع ملف أولاً!"
    with open(file.name, "rb") as f:
        content = f.read()
    text = process_pdf(content)
    summary = generate_summary(text)
    return summary

with gr.Blocks(title="PDF Summarizer") as demo:
    gr.Markdown("# 📄 PDF Summarizer")
    gr.Markdown("ارفع ملف PDF واحصل على ملخص فوري!")
    
    with gr.Row():
        file_input = gr.File(label="ارفع ملف PDF", file_types=[".pdf"])
    
    summarize_btn = gr.Button("📝 لخص الملف", variant="primary")
    summary_output = gr.Textbox(label="الملخص", interactive=False, lines=15)
    
    summarize_btn.click(
        fn=handle_pdf,
        inputs=[file_input],
        outputs=[summary_output]
    )

demo.launch()
