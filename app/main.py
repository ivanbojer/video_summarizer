import gradio as gr
from app import video_summarizer as vid
import json
from app import ignoreSSL
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.requests import Request

# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

def summarize_text(video_id, progress=gr.Progress()):
    progress(float(0.0), desc="Starting...")
    summary = vid.test_load_final_summary()
    # summary = vid.transcribe_video(video_id, False, progress)
    return summary 

with gr.Blocks() as demo:
    with gr.Column():
        with gr.Group():
            inp = gr.Text(label="Video id:")
            btn = gr.Button("Transcribe")
        with gr.Box():
            out = gr.TextArea(label="Summary output:")
        
        btn.click(fn=summarize_text, inputs=inp, outputs=out)


app = FastAPI()

@app.get('/')
async def homepage(request: Request):
    return RedirectResponse(url='/gradio')

gradio_app = gr.mount_gradio_app(app, demo.queue(), '/gradio')

def main():
    if config_details['IGNORE_SSL']:
        print ( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():
            demo.queue()
    else:
        demo.queue().launch()


if __name__ == "__main__":
    main()
    