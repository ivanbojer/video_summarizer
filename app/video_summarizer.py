from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
from app import ignoreSSL
from app import my_prompt as PROMPT
from app import whisper_mgr as whisper
from app import chunk_media as file_chunker
from app import tweeter_mgr as TweeterMgr
from app import logger
from app import mgr_openai as MyOpenAI
from app import my_helper as HELPER
import datetime
import time
import os

import json
import tiktoken

FILE_SUMMARY_BATCHES = "temp_data/temp_summary_batches.txt"
FILE_SUMMARY_BATCHES_RESPONSES = "temp_data/temp_summary_batches_responses.txt"
FILE_FINAL_SUMMARY = "temp_data/video_FINAL_SUMMARY.txt"
FILE_VIDEO_SUBTITLES = "temp_data/temp_video_subtitles.txt"
FILE_VIDEO_SUBTITLES_RAW = "temp_data/temp_video_subtitles-raw.txt"

DEBUG = True
SLEEP_SECONDS = 25

enc = None

# Load config values
with open(r"config.json") as config_file:
    config_details2 = json.load(config_file)


def num_tokens_from_string(string: str) -> int:
    global enc

    if not enc:
        enc = tiktoken.encoding_for_model(config_details2["OA_CHAT_GPT_MODEL"])

    """Returns the number of tokens in a text string."""
    num_tokens = len(enc.encode(string))

    return num_tokens


def download_transcript(video_id, progress=None):
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function
    prog = 0.2
    if progress != None:
        progress(prog, "Downloading video")

    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled as e:
        logger.logger.warning(
            "Transcripts not enabled of not generated. Falling back to whisper..."
        )
        file_name = whisper.download_audio(video_id)
        file_chunk_names = file_chunker.chunk_audio_file(
            audio_file_path=file_name, progress=progress
        )

        translation_txt = ""
        for count, file in enumerate(file_chunk_names):
            file_translation = whisper.transcribe_audio(file)
            if progress != None:
                progress(
                    prog,
                    "Transcribing video segment {} of {}".format(
                        count + 1, len(file_chunk_names)
                    ),
                )
                prog = prog + 0.03
            if DEBUG:
                with open(FILE_VIDEO_SUBTITLES, "a") as f_out:
                    f_out.write(file_translation)

            translation_txt = translation_txt + file_translation

        return translation_txt, None

    # creating or overwriting a file "subtitles.txt" with
    # the info inside the context manager
    text = text_raw = ""
    for i in srt:
        text_raw = text_raw + "{}\n".format(i)
        text = text + " {} ".format(i["text"])

    return text, text_raw


def get_transcript_summaries(transcript, batch_prompt, progress=None):
    # for debugging purposes
    HELPER.SAVE_FILE(
        "{}\n".format(datetime.datetime.now()), FILE_SUMMARY_BATCHES, append=True
    )
    HELPER.SAVE_FILE(
        "{}\n".format(datetime.datetime.now()),
        FILE_SUMMARY_BATCHES_RESPONSES,
        append=True,
    )
    words = transcript.split(" ")

    # MAX_WORDS = 750 * 7 - len(batch_prompt.split(" "))
    # 25000 words is about 20000 tokens (limitation per minute)
    MAX_WORDS = 17000 - len(batch_prompt.split(" "))
    logger.logger.info('Max words is: {}'.format( MAX_WORDS ))

    batches = []
    for i in range(0, len(words), MAX_WORDS):
        transcript_snippet = " ".join(words[i : i + MAX_WORDS])
        single_batch = '"""{}"""'.format(transcript_snippet)
        batches.append(single_batch)
        HELPER.SAVE_FILE("{}\n".format(single_batch), FILE_SUMMARY_BATCHES, append=True)

    prog = 0.5
    total_time = 0
    start = time.time()
    total_batches = len(batches)
    responses = []
    for i, single_batch in enumerate(batches):
        logger.logger.info("AI processing batch {} of {}".format(i + 1, total_batches))
        if progress != None:
            progress(prog, "AI processing batch {} of {}".format(i + 1, total_batches))
            prog = prog + 0.03

        w_len = batch_prompt + single_batch
        logger.logger.info('Processing {} words == {} tokens'.format( len( w_len.split(' ') ), num_tokens_from_string(w_len)))

        response = MyOpenAI.completions_with_backoff(
            system_prompt=batch_prompt, user_prompt=single_batch
        )

        end = time.time()
        response = "<summary>{}</summary>\n".format(HELPER.FIX_TEXT(response))
        responses.append(response)
        HELPER.SAVE_FILE(response, FILE_SUMMARY_BATCHES_RESPONSES, append=True)
        logger.logger.info(
            "Batch #{}: elapsed time {}s".format(i + 1, round(end - start))
        )
        total_time = total_time + round(end - start)
        start = end

    logger.logger.info("Total elapsed time (for all batches) {}s".format(total_time))

    return "\n".join(responses)


def get_final_summary(summary_batches, prompt, video_id, progress=None):
    if progress != None:
        progress(0.9, "Creating final summary...")
    logger.logger.info("Creating final summary")
    start = time.time()
    final_summary_txt = MyOpenAI.completions_with_backoff(
        system_prompt=prompt, user_prompt="\n".join(summary_batches)
    )
    logger.logger.info("Elapsed time {}s".format(round(time.time() - start)))
    if progress != None:
        progress(1.0, "Done")

    s1 = datetime.datetime.now().strftime("%Y%m%d.%H%M%S")
    path_parts = FILE_FINAL_SUMMARY.split("/")
    with open(
        "{}/{}-{}-{}".format(path_parts[0], s1, video_id, path_parts[1]), "w"
    ) as f_out:
        f_out.write(final_summary_txt)

    return final_summary_txt


# def test_twitter():
#     # Twitter testing
#     final_summary_txt = ""
#     with open('20230928.221655-iU1kRlrEJUI-video_FINAL_SUMMARY.txt', 'r') as file:
#         final_summary_txt = file.read()

#     text, unnused = extract_tldr_section( final_summary_txt )
#     logger.logger.info( 'TL;DR:\n{}'.format( text ) )

#     # tw_mgr = TweeterMgr()
#     ## tw_mgr.post_tweet( text_blog, title )


def clean_up_temp_files():
    logger.logger.info("Removing temp .mp3 files...")
    try:
        path = "./"
        files = os.listdir(path)

        for f in files:
            if f.endswith(".mp3"):
                os.remove(os.path.join(path, f))
    except Exception as e:
        logger.logger.warning("No mp3 files: {}".format(e))


def transcribe_video(video_id, batch_prompt, final_prompt, json=False, progress=None):
    transcript, transcript_raw = download_transcript(video_id, progress)
    
    # for debugging purposes
    HELPER.SAVE_FILE(transcript, FILE_VIDEO_SUBTITLES)
    HELPER.SAVE_FILE(transcript_raw, FILE_VIDEO_SUBTITLES_RAW)
    logger.logger.info(
        "nr. of tokens: {}, transcript length: {}".format(
            num_tokens_from_string(transcript), len(transcript)
        )
    )

    summary_batches = get_transcript_summaries(
        transcript=transcript, batch_prompt=batch_prompt, progress=progress
    )

    # # ### PROMPT TESTING
    # summary_batches = HELPER.OPEN_FILE(FILE_SUMMARY_BATCHES_RESPONSES)
    # summary_batches = HELPER.FIX_TEXT( summary_batches )
    ###

    final_summary_txt = get_final_summary(
        summary_batches=summary_batches,
        prompt=final_prompt,
        video_id=video_id,
        progress=progress,
    )

    # clean up the file
    clean_up_temp_files()

    if not json:
        return final_summary_txt
    else:
        json_str = {"video_id": video_id, "summary": final_summary_txt}
        return json.loads(json_str)
