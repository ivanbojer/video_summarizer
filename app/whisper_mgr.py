from __future__ import unicode_literals
import yt_dlp as downloader
import openai
import json
import os
from app import ignoreSSL
from app import logger

file_name = None
AI_API_KEY = os.getenv("AI_API_KEY") or None

if AI_API_KEY is None:
    raise BaseException("Missing sec configuration (whisper_mgr)")

with open(r"config.json") as config_file:
    config_details2 = json.load(config_file)


def yt_dlp_monitor(d):
    global file_name
    if d["status"] == "finished":
        file_name = d["filename"]
        logger.logger.info(
            "Done downloading\n{}\n, now converting ...".format(file_name)
        )


MEDIA_FILENAME = "temp_audio_file.mp3"
TRANSLATION_FILENAME = "temp_audio_file_transcript.txt"


def transcribe_audio(file_name=MEDIA_FILENAME):
    logger.logger.info("Transcribing file_name: {}".format(file_name))
    f_media = open(file_name, "rb")

    response = openai.Audio.transcribe(
        api_key=AI_API_KEY,
        model=config_details2["OA_AUDIO_MODEL"],
        file=f_media,
        response_format="text",  # text, json, srt, vtt
    )

    return response


def download_audio(video_id):
    ydl_opts = {
        "format": "bestaudio/best",
        "progress_hooks": [yt_dlp_monitor],  # here's the function we just defined
        # 'logger': MyLogger(),
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "96",
            }
        ],
    }

    with downloader.YoutubeDL(ydl_opts) as ydl:
        logger.logger.info(
            "Video URL: https://www.youtube.com/watch?v={}".format(video_id)
        )
        ydl.download(["https://www.youtube.com/watch?v={}".format(video_id)])

    global file_name

    extension = "." + file_name.split(".")[-1]
    file_name = file_name.replace(extension, ".mp3")
    return file_name


def main():
    file_name = download_audio("1AbToBYhY20")
    translation_txt = transcribe_audio(file_name)
    logger.logger.info(translation_txt)

    with open(TRANSLATION_FILENAME, "w") as f_out:
        f_out.write(translation_txt)


if __name__ == "__main__":
    if config_details2["IGNORE_SSL"]:
        logger.logger.warn("ignore SSL")
        with ignoreSSL.no_ssl_verification():
            main()
    else:
        main()
