from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
from app import ignoreSSL
from app import my_prompt as PROMPT
from app import whisper_mgr as whisper
from app import chunk_media as file_chunker
from app import tweeter_mgr as TweeterMgr
from app import logger
import datetime
import time
import os

import openai
import json
import tiktoken

FILE_SUMMARY_BATCHES = "temp_data/temp_summary_batches.txt"
FILE_FINAL_SUMMARY = "temp_data/video_FINAL_SUMMARY.txt"
FILE_VIDEO_SUBTITLES = "temp_data/temp_video_subtitles.txt"
FILE_VIDEO_SUBTITLES_RAW = "temp_data/temp_video_subtitles-raw.txt"

DEBUG = True
SLEEP_SECONDS = 25


enc = None

# Load config values
with open(r'config.json') as config_file:
    config_details2 = json.load(config_file)
# //os.getenv("OPENAI_API_KEY")
AI_API_KEY = os.getenv('AI_API_KEY') or None

if AI_API_KEY is None:
    raise BaseException('Missing sec configuration (video_summarizer)')

openai.api_key = AI_API_KEY

def save_file( file_name, content):
    if file_name:
        with open(file_name, "w") as f_out:
            f_out.write( content )


def get_completion(prompt, file_name=None, model=config_details2['OA_CHAT_GPT_MODEL']):
    logger.logger.info("nr. of tokens: {}, string len: {}".format( num_tokens_from_string(prompt), len(prompt) ))
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output,
        # engine=config_details['MS_CHAT_GPT_MODEL']
    )

    if file_name:
        f_out = open(file_name, "w")
        f_out.write( response.choices[0].message["content"] )
        f_out.close()

    return response.choices[0].message["content"]


def num_tokens_from_string(string: str) -> int:
    global enc

    if not enc:
        enc = tiktoken.encoding_for_model( config_details2['OA_CHAT_GPT_MODEL'] )

    """Returns the number of tokens in a text string."""
    num_tokens = len(enc.encode(string))

    return num_tokens


def print_response(prompt, text=None):
    response = get_completion(prompt)
    logger.logger.info(response)


def download_transcript(video_id, progress=None): 
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function
    prog = 0.2
    if progress != None:
        progress(prog, 'Downloading video')

    try:
        srt = YouTubeTranscriptApi.get_transcript( video_id )
    except TranscriptsDisabled as e:
        logger.logger.warning( "Transcripts not enabled of not generated. Falling back to whisper...")
        file_name = whisper.download_audio( video_id )
        file_chunk_names = file_chunker.chunk_audio_file( audio_file_path=file_name, progress=progress )

        translation_txt = ""
        for count,file in enumerate(file_chunk_names):
            file_translation = whisper.transcribe_audio( file  )
            if progress != None:
                progress(prog, 'Transcribing video segment {} of {}'.format( count+1, len(file_chunk_names)))
                prog = prog + 0.03
            if DEBUG:
                with open(FILE_VIDEO_SUBTITLES, "a") as f_out:
                    f_out.write( file_translation )

            translation_txt = translation_txt + file_translation

        return translation_txt, None

    # creating or overwriting a file "subtitles.txt" with
    # the info inside the context manager
    text = text_raw = ''
    for i in srt:
        text_raw = text_raw + "{}\n".format(i)
        text = text + " {} ".format(i['text'])

    return text, text_raw


def test_load_summary_batches():
    with open(FILE_SUMMARY_BATCHES, 'r') as file:
        text = file.read()

    return text


def test_load_final_summary():
    logger.logger.info('Loading dummy summary...')
    time.sleep( 2 )
    with open(FILE_FINAL_SUMMARY, 'r') as file:
        text = file.read()

    return text


def summarize_transcript_in_batches( text, batch_promp, progress=None ):
    if DEBUG:
            with open(FILE_SUMMARY_BATCHES, 'w') as f_out:
                f_out.write( 'Date: {}\n\n'.format( datetime.datetime.now() ) )

    summary_batches = []

    # Setting batch size and context size
    batch_size = 2500

    # Tokenize the script
    script_tokens = text.split(" ")

    total_batches = round(len(script_tokens)/batch_size)

    count = 0
    prog = 0.5
    start = time.time()
    cummulative_time = 0
    average_processing_time = 0
    for i in range(0, len(script_tokens), batch_size):
        text_to_edit = " ".join(script_tokens[i:i+batch_size])

        # print_response(prompt, text)
        logger.logger.info( "AI processing batch {} of {}".format( count+1, total_batches ) )
        if progress != None:
            progress(prog, "AI processing batch {} of {}".format( count+1, total_batches ))
            prog = prog + 0.03

        response = get_completion( '{}\n---\n{}'.format( batch_promp, text_to_edit ))

        if DEBUG:
             with open(FILE_SUMMARY_BATCHES, "a") as f_out:
                f_out.write( "- {}\n".format( response ) )

        summary_batches.append( "- {}\n".format( response ) )
        
        end = time.time()
        time_elapsed = round(end - start)
        average_processing_time = ( average_processing_time+time_elapsed) / 2.0
        cummulative_time = cummulative_time + time_elapsed
        logger.logger.info('Time elapsed --> single_batch {}s average {}s cumulative {}s'.format( time_elapsed,average_processing_time,cummulative_time ))
        
        count = count + 1
        if count % 3 == 0:
            logger.logger.info('Sleep {} seconds'.format( SLEEP_SECONDS ))
            time.sleep( SLEEP_SECONDS )

        start = end

    return ''.join(summary_batches)


def __extract_section( text, header ):

    # first find the beginnig of the blog
    # add title to it too as we have set format
    start = text.index(header)
    start = start + len (header)
    end = text.index( '\n', start)

    # get the title
    title = text[start:end]
    # skip the title and find the end of text
    start = start + len(title) + 2 #2 escapes
    end = text.index('\'\'\'', start)

    return title, text[start:end]


def create_final_summary(text, final_prompt, progress=None):
    logger.logger.info("Creating final summary...")
    if progress != None:
        progress(0.9, 'Creating final summary...')

    response = get_completion( '{}\n---\n{}'.format( final_prompt, text ) )
    logger.logger.info('Done!')

    if progress != None:
        progress(1, 'Done')

    return response


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
    logger.logger.info('Removing temp .mp3 files...')
    try:
        path = './'
        files = os.listdir(path)
        
        for f in files:
            if f.endswith('.mp3'):
                os.remove( os.path.join(path, f) )
    except Exception as e:
        logger.logger.warning('No mp3 files: {}'.format( e ))

def transcribe_video(video_id, batch_prompt, final_prompt, json=False, progress=None):
    transcript, transcript_raw = download_transcript( video_id, progress )
    logger.logger.info("nr. of tokens: {}, transcript length: {}".format( num_tokens_from_string(transcript), len(transcript) ))

    summary_batches = summarize_transcript_in_batches( text=transcript, batch_promp=batch_prompt, progress=progress )

    # # ### PROMPT TESTING
    # summary_batches = load_summary_batches() 
    ###

    final_summary_txt = create_final_summary( text=summary_batches, final_prompt=final_prompt, progress=progress )
    s1 = datetime.datetime.now().strftime("%Y%m%d.%H%M%S")
    path_parts = FILE_FINAL_SUMMARY.split('/')
    with open('{}/{}-{}-{}'.format( path_parts[0], s1, video_id, path_parts[1] ), "w") as f_out:
            f_out.write( final_summary_txt )

    #clean up the file
    clean_up_temp_files()

    if not json:
        return final_summary_txt
    else:
        json_str = {"video_id": video_id, "summary":final_summary_txt}
        return json.loads( json_str )


def main():
    VIDEO_ID = 'TnyMFI0uoXY'
    summary = transcribe_video(VIDEO_ID)

    # test_twitter()

if __name__ == "__main__":
    if config_details2['IGNORE_SSL']:
        logger.logger.warn( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():
            main()
    else:
        main()
