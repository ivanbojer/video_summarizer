from fastapi import FastAPI
import uvicorn
import json
import datetime as dt
import gradio as gr
import time
import random

import video_summarizer as vid
 
app = FastAPI()
count = 0
 
@app.get("/")
def root ():
  return {"message": "Hello World!"}


@app.get("/transcribe_video/{video_id}")
def read_course(video_id):
    global count
    # summary = vid.transcribe_video(video_id)
    summary = vid.test_load_final_summary()

    json_dict = {"video_id": video_id, "summary":summary, "time": str(dt.datetime.now()), "count":count}
    count = count + 1

    return json.dumps( json_dict, indent=4 )  


@app.get('/test')
async def balabala():
    import gradio as gr

    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        def user(user_message, history):
            return "", history + [[user_message, None]]

        def bot(history):
            bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
            history[-1][1] = ""
            for character in bot_message:
                history[-1][1] += character
                time.sleep(0.05)
                yield history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    global app 
    demo.queue()
    demo.startup_events()
    app = gr.mount_gradio_app(app, demo, f'/gradio')

# def greet(name):
#    return "Hello " + name


# demo = gr.Interface(fn=greet, inputs="text", outputs="text")
# demo.launch(share=False)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)