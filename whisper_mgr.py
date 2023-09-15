from __future__ import unicode_literals
import yt_dlp as downloader
import openai
import json
import ignoreSSL

file_name = None

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def yt_dlp_monitor(d):
    global file_name
    if d['status'] == 'finished':
        file_name = d['filename']
        print('Done downloading\n{}\n, now converting ...'.format( file_name ))

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
        "progress_hooks": [yt_dlp_monitor],  # here's the function we just defined
        # 'logger': MyLogger(),
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }


    with downloader.YoutubeDL(ydl_opts) as ydl:
        print( "Video URL: https://www.youtube.com/watch?v={}".format( video_id ) )
        ydl.download(["https://www.youtube.com/watch?v={}".format( video_id )])

    global file_name
    return file_name    


def main():
    file_name = download_audio( '1AbToBYhY20' )
    translation_txt = transcribe_audio( file_name  )
    print ( translation_txt )

    with open(TRANSLATION_FILENAME, 'w') as f_out:
        f_out.write( translation_txt )


if __name__ == "__main__":
    if config_details['IGNORE_SSL']:
        print ( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():
             main()
    else:
        main()