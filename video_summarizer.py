from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
import ignoreSSL
import whisper_mgr as whisper

import openai
import json
import tiktoken

FILE_SUMMARY_BATCHES = "temp_summary_batches.txt"
FILE_FINAL_SUMMARY = "temp_FINAL_SUMMARY.txt"
FILE_VIDEO_SUBTITLES = "temp_video_subtitles.txt"
FILE_VIDEO_SUBTITLES_RAW = "temp_video_subtitles-raw.txt"

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


def download_transcript(video_id="hlNHL5H5FtI"): 
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function

    try:
        srt = YouTubeTranscriptApi.get_transcript( video_id )
    except TranscriptsDisabled as e:
        print( "Transcripts not enabled of not generated. Falling back to whisper...")
        file_name = whisper.download_audio( video_id )
        translation_txt = whisper.transcribe_audio( file_name  )

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
    batch_size = 3000

    # Tokenize the script
    script_tokens = text.split(" ")

    count = 0
    for i in range(0, len(script_tokens), batch_size):
        text_to_edit = " ".join(script_tokens[i:i+batch_size])

        prompt = f"""
        The text delimited by triple backticks in the context that it \
        is a youtube script for a narrated video. The video itself contains daily \
        updates on the stock market and personal stories. Summarise the text. Extract any updates about any particular stock \
        or any company mentioned and in particular Gamestop (ticker: GME). Look for \
        any strategies on how to trade options or mention of the name 'Ryan Cohen'.
        
        Text:
        ```{text_to_edit}```
        """

        # print_response(prompt, text)
        print ("Batch #{}".format( count ) )
        response = get_completion(prompt)
        summary_batches.append( "- {}\n".format( response ) )

        count = count + 1
        
        # if count > 1:
        #     break

    return ' '.join(summary_batches)


def create_final_summary(text):
    print ("Creating final summary...")

    #     7 - Provide same steps as JSON string with \
    # the following keys: title, long_summary, performance, sentiment, emotions
    prompt = f"""
    You are given multiple summaries one per line starting with a dash for \
    youtube script for a narrated video that talks about stock market. The content \
    is delimited with triple backticks
    1 - Create title out of the main focus in the text.
    2 - Summarize the text between 100 and 200 words and focusing on any aspects that \
    are relevant to future potential of any company mentioned and especially Gamestop.
    3 - Extract relevant information to any future company performance.
    4 - What is the general sentiment of the text? Format your answer as a list of \
    lower-case words separated by commas.
    5 - Identify a list of emotions in the text? Format your answer as a list of \
    lower-case words separated by commas.
    6 - Write Key Notes from the summary
    7 - Write a Step-by-Step Guide from the Notes
    8 - Write a Blog post from the Notes
    9 - Create Midjourney prompts from the Notes
    10 - Create DALLE prompts from the Notes
    
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

    Emotions:
    '''
    Step 5 here
    '''

    Key Notes:
    '''
    Step 6 here
    '''

    Step-by-step guide:
    '''
    Step 7 here
    '''

    Blog post:
    '''
    Step 8 here
    '''

    Midjourney prompts:
    '''
    Step 9 here
    '''

    DALLE prompts:
    '''
    Step 10 here
    '''

    Text:
    ```{text}```
    """

    response = get_completion(prompt, file_name=FILE_FINAL_SUMMARY)
    print ("Done [filename: {}]!".format(FILE_FINAL_SUMMARY) )

    return response


def main():
    DEBUG = True

    transcript, transcript_raw = download_transcript( '1AbToBYhY20' ) # 'w4WcTX-PNtU' subtitles not ready 99tkOvP3QAA - short

    print ("nr. of tokens: {}, transcript length: {}".format( num_tokens_from_string(transcript), len(transcript) ))
    summary_batches = summarize_transcript_in_batches( transcript )

    response = create_final_summary( summary_batches )

    with open(FILE_FINAL_SUMMARY, "w") as f_out:
            f_out.write( response )

    if DEBUG:
        with open(FILE_VIDEO_SUBTITLES, "w") as f_out:
            f_out.write( transcript )

        with open(FILE_SUMMARY_BATCHES, "w") as f_out:
            f_out.write( summary_batches )

    # import whisper_mgr as w

    # transcription = w.transcribe_audio( '99tkOvP3QAA.mp3' )
    # response = create_final_summary( transcription )
    # print (response )

if __name__ == "__main__":
    if config_details['IGNORE_SSL']:
        print ( "ignore SSL" )
        with ignoreSSL.no_ssl_verification():
            main()
    else:
        main()
