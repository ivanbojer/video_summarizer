from app import my_prompt as PROMPT
from app import video_summarizer as app
from app import mgr_tweeter as twr_mgr
import json

# VIDEO_ID = '-YjSXZGLgAY' #TnyMFI0uoXY'
# summary_str_arr = app.transcribe_video( VIDEO_ID,
#                                 PROMPT.UNCLE_SYSTEM_PROMPT_FINAL_JSON)

# summary_json = json.loads( summary_str_arr[0] )
# pretty_json = json.dumps( summary_json, indent=4 )
# print( pretty_json )

tweet = input('Do you want to tweet this [y]? ') or 'y'

summary_json = None
with open('temp_data/20241008.155901--YjSXZGLgAY-video_FINAL_SUMMARY.txt', 'r') as f:
    summary_json = json.load(f)


if (tweet == 'y'):
    twr = twr_mgr.TweeterMgr()
    twr.post_tweet(summary_json['BLOG'], summary_json['TITLE'], False)
