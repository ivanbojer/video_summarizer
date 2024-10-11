from app import my_prompt as PROMPT
from app import video_summarizer as app
from app import mgr_tweeter as twr_mgr
import json

summary_json = None

VIDEO_ID = 'VPq6UnNtDBo' #TnyMFI0uoXY'
final_summary_txt, cost, json_str = app.transcribe_video( VIDEO_ID,
                                              PROMPT.UNCLE_SYSTEM_PROMPT_FINAL_JSON)

summary_json = json.loads( final_summary_txt[0] )
pretty_json = json.dumps( summary_json, indent=4 )
print( pretty_json )

tweet = input('Do you want to tweet this [y]? ') or 'y'


# with open('temp_data/20241008.155901--YjSXZGLgAY-video_FINAL_SUMMARY.txt', 'r') as f:
#     summary_json = json.load(f)

original_url = f'https://www.youtube.com/watch?v={VIDEO_ID}'
print( f'original_url: {original_url}')
if (tweet == 'y'):
    twr = twr_mgr.TweeterMgr()
    twr.post_tweet(summary_json['BLOG'], summary_json['TITLE'], False)
