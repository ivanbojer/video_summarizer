from app import my_prompt as PROMPT
from app import video_summarizer as app
import json

VIDEO_ID = '-YjSXZGLgAY' #TnyMFI0uoXY'
summary = app.transcribe_video(VIDEO_ID,
                               PROMPT.UNCLE_SYSTEM_PROMPT_FINAL)

pretty_json = json.dumps( summary, indent=4 )
print( pretty_json )


