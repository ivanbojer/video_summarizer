from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
import ignoreSSL
import whisper_mgr as whisper
import chunk_media as file_chunker
from tweeter_mgr import TweeterMgr
import datetime
import time

import openai
import json
import tiktoken

FILE_SUMMARY_BATCHES = "temp_data/temp_summary_batches.txt"
FILE_FINAL_SUMMARY = "temp_data/video_FINAL_SUMMARY.txt"
FILE_VIDEO_SUBTITLES = "temp_data/temp_video_subtitles.txt"
FILE_VIDEO_SUBTITLES_RAW = "temp_data/temp_video_subtitles-raw.txt"

DEBUG = True
SLEEP_SECONDS = 30


enc = None

# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)
# //os.getenv("OPENAI_API_KEY")
openai.api_key = config_details['OA_OPENAI_API_KEY']
# openai.api_base = config_details['MS_OPENAI_API_BASE']
# openai.api_version = config_details['MS_OPENAI_API_VERSION']
# openai.api_type = config_details['MS_OPENAI_API_TYPE']


def save_file( file_name, content):
    if file_name:
        with open(file_name, "w") as f_out:
            f_out.write( content )

        
# gpt-3.5-turbo-16k
# gpt-3.5-turbo
# gpt-4
def get_completion(prompt, file_name=None, model=config_details['OA_CHAT_GPT_MODEL']):
    print ("nr. of tokens: {}, string len: {}".format( num_tokens_from_string(prompt), len(prompt) ))
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
        enc = tiktoken.encoding_for_model( config_details['OA_CHAT_GPT_MODEL'] )

    """Returns the number of tokens in a text string."""
    num_tokens = len(enc.encode(string))

    return num_tokens


def print_response(prompt, text=None):
    response = get_completion(prompt)
    print(response)


def download_transcript(video_id): 
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function

    try:
        srt = YouTubeTranscriptApi.get_transcript( video_id )
    except TranscriptsDisabled as e:
        print( "Transcripts not enabled of not generated. Falling back to whisper...")
        file_name = whisper.download_audio( video_id )
        file_chunk_names = file_chunker.chunk_audio_file( audio_file_path=file_name )

        ## If something breaks with whisper we need to re-populate array mannualy
        # file_chunk_names = [ 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_1.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_2.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_3.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_4.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_5.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_6.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_7.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_8.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_9.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_10.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_11.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_12.mp3',
                            # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_13.mp3']

        translation_txt = ""
        for file in file_chunk_names:
            file_translation = whisper.transcribe_audio( file  )
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


def load_summary_batches():
    with open(FILE_SUMMARY_BATCHES, 'r') as file:
        text = file.read()

    return text


def summarize_transcript_in_batches( text ):
    summary_batches = []

    # Setting batch size and context size
    batch_size = 2500

    # Tokenize the script
    script_tokens = text.split(" ")

    count = 0
    start = time.time()
    for i in range(0, len(script_tokens), batch_size):
        text_to_edit = " ".join(script_tokens[i:i+batch_size])

        prompt = f"""
        The text delimited by triple backticks in the context for \
        a Youtube transcript for a narrated video that talks about stock market. \
        The narrator name is Uncle Bruce. The transcript itself contains daily \
        updates on the stock market and Bruce's personal stories. Summarise the text. \
        Extract any updates about any particular stock or any company mentioned and in \
        particular Gamestop (ticker: GME). Look for any options strategies on how to \
        trade options. Extract any information mentioned about 'Ryan Cohen', the CEO of GameStop.
        
        Text:
        ```{text_to_edit}```
        """

        # print_response(prompt, text)
        print ("Batch #{}".format( count ) )
        response = get_completion(prompt)

        if DEBUG:
             with open(FILE_SUMMARY_BATCHES, "w") as f_out:
                f_out.write( "- {}\n".format( response ) )

        summary_batches.append( "- {}\n".format( response ) )

        count = count + 1

        if count % 3 == 0:
            print ('Sleep {} seconds'.format( SLEEP_SECONDS ))
            time.sleep( SLEEP_SECONDS )
        
        end = time.time()
        print ('Time elapsed: {}s\n'.format( round(end - start) ))
        start = end
        # if count > 1:
        #     break

    return ' '.join(summary_batches)


def extract_tldr_section( text ):
    HEADER = 'Conclusion:\n'

    return __extract_section( text, HEADER )


def extract_blog_section( text ):
    HEADER = 'Blog post:\n\'\'\'\nTitle:'

    return __extract_section( text, HEADER )


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


def create_final_summary(text):
    print ("Creating final summary...")

    #     7 - Provide same steps as JSON string with \
    # the following keys: title, long_summary, performance, sentiment, emotions
    prompt = f"""
    You are given multiple summaries one per line starting with a dash for \
    youtube script for a narrated video that talks about stock market. All the summaries are 
    part of the same narration. The narrator \
    name is Uncle Bruce. The content is delimited with triple backticks. Perform the following:
    1 - Create title out of the main focus in the text.
    2 - Summarize the text focusing on any aspects that \
    are relevant to future potential of any company mentioned and especially Gamestop.
    3 - Extract relevant information to any future company performance.
    4 - What is the general sentiment of the text? Format your answer as a list of \
    lower-case words separated by commas.
    5 - Write Key Notes from the summary
    6 - Write a Twitter blog post
    7 - Create Midjourney prompts for Key Notes
    
    Use the following format:

    Title:
    '''
    Step 1 here
    '''
 
    Summary:
    '''
    Step 2 here
    '''

    Performance:
    '''
    Step 3 here
    '''

    Sentiment:
    '''
    Step 4 here
    '''

    Key Notes:
    '''
    Step 5 here
    '''

    Blog post:
    '''
    Step 6 here
    '''

    Midjourney prompts:
    '''
    Step 7 here
    '''

    Text:
    ```{text}```
    """

    response = get_completion(prompt)
    print ('Done!')

    return response


def test_twitter():
    # Twitter testing
    final_summary_txt = ""
    with open('20230928.221655-iU1kRlrEJUI-video_FINAL_SUMMARY.txt', 'r') as file:
        final_summary_txt = file.read()

    text, unnused = extract_tldr_section( final_summary_txt )
    print( 'TL;DR:\n{}'.format( text ) )

    # tw_mgr = TweeterMgr()
    ## tw_mgr.post_tweet( text_blog, title )


def main():
    VIDEO_ID = 'ooOlEd5HxWs'

    transcript, transcript_raw = download_transcript( VIDEO_ID )
    print ("nr. of tokens: {}, transcript length: {}".format( num_tokens_from_string(transcript), len(transcript) ))

    summary_batches = summarize_transcript_in_batches( transcript )

    # # ### PROMPT TESTING
    # summary_batches = load_summary_batches() 
    ###

    final_summary_txt = create_final_summary( summary_batches )

    s1 = datetime.datetime.now().strftime("%Y%m%d.%H%M%S")
    path_parts = FILE_FINAL_SUMMARY.split('/')
    with open('{}/{}-{}-{}'.format( path_parts[0], s1, VIDEO_ID, path_parts[1] ), "w") as f_out:
            f_out.write( final_summary_txt )

    # test_twitter()

if __name__ == "__main__":
    if config_details['IGNORE_SSL']:
        print ( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():
            main()
    else:
        main()
