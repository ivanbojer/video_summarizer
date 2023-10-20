from app import my_prompt as PROMPT
from app import video_summarizer as app

VIDEO_ID = '1yE0L1QZ8BQ' #TnyMFI0uoXY'
summary = app.transcribe_video(VIDEO_ID,
                               PROMPT.SYSTEM_PROMPT_BATCHES,
                               PROMPT.SYSTEM_PROMPT_FINAL)



