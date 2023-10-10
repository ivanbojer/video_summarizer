import gradio as gr
import video_summarizer as vid
import json
import datetime as dt
import time

def summarize_text(video_id, progress=gr.Progress()):
    progress(float(0.0), desc="Starting...")
    # summary = vid.test_load_final_summary()
    summary = vid.transcribe_video('TnyMFI0uoXY', False, progress)
    return summary 

with gr.Blocks() as demo:
    with gr.Column():
        with gr.Group():
            inp = gr.Text(label="Video id:")
            btn = gr.Button("Transcribe")
        with gr.Box():
            out = gr.TextArea(label="Summary output:")
        

        btn.click(fn=summarize_text, inputs=inp, outputs=out)
    

if __name__ == "__main__":
    demo.queue().launch(share=False)