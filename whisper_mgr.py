from __future__ import unicode_literals
import youtube_dl
import openai
import json
import ignoreSSL

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

with open(r'config.json') as config_file:
    config_details = json.load(config_file)

MEDIA_FILENAME = 'temp_audio_file.mp3'
TRANSLATION_FILENAME = 'temp_audio_file_transcript.txt'

def transcribe_audio( file_name = MEDIA_FILENAME ):
    f_media = open( file_name, 'rb')

    response = openai.Audio.transcribe(
        api_key = config_details['OA_OPENAI_API_KEY'],
        model = config_details['OA_AUDIO_MODEL'],
        file = f_media,
        response_format = 'text' # text, json, srt, vtt
    )

    return response


def download_audio( video_id ):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        # 'postprocessor_args': [
        #     '-ar', '16000'
        # ],
        'prefer_ffmpeg': True,
        'keepvideo': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print( "Video URL: https://www.youtube.com/watch?v={}".format( video_id ) )
        ydl.download(["https://www.youtube.com/watch?v={}".format( video_id )])



def main():
    if config_details['IGNORE_SSL']:
        print ( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():

            # download_audio( '99tkOvP3QAA' )
            translation_txt = transcribe_audio( '99tkOvP3QAA.mp3'  )

            with open(TRANSLATION_FILENAME, 'w') as f_out:
                f_out.write( translation_txt )

            print ( translation_txt )


if __name__ == "__main__":
    main()