from youtube_transcript_api import YouTubeTranscriptApi
import ignoreSSL

import openai
import os
import json
import tiktoken

FILE_SUMMARY_BATCHES = "temp_summary_batches.txt"
FILE_FINAL_SUMMARY = "temp_FINAL_SUMMARY.txt"
FILE_VIDEO_SUBTITLES = "temp_video_subtitles.txt"
FILE_VIDEO_SUBTITLES_RAW = "temp_video_subtitles-raw.txt"

enc = None

# Load config values
with open(r'config-openai.json') as config_file:
    config_details = json.load(config_file)
# //os.getenv("OPENAI_API_KEY")
openai.api_key = config_details['OPENAI_API_KEY']
# openai.api_base = config_details['OPENAI_API_BASE']
# openai.api_version = config_details['OPENAI_API_VERSION']
# openai.api_type = config_details['OPENAI_API_TYPE']

# gpt-3.5-turbo-16k
# gpt-3.5-turbo
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output,
        # engine=config_details['CHAT_GPT_MODEL']
    )
    return response.choices[0].message["content"]


def num_tokens_from_string(string: str) -> int:
    global enc

    if not enc:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

    """Returns the number of tokens in a text string."""
    num_tokens = len(enc.encode(string))

    return num_tokens


def print_response(prompt, text=None):
    response = get_completion(prompt)
    print(response)


def download_transcript(video_id="hlNHL5H5FtI"): 
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function
    # NhqYqVZLC1A
    # w4WcTX-PNtU
    # hlNHL5H5FtI&t=22s
    srt = YouTubeTranscriptApi.get_transcript( video_id )
    
    # prints the result
    # print(srt)

    # creating or overwriting a file "subtitles.txt" with
    # the info inside the context manager
    with open(FILE_VIDEO_SUBTITLES, "w") as f:
        f_raw = open(FILE_VIDEO_SUBTITLES_RAW, "w")
        # iterating through each element of list srt
        for i in srt:
            # writing each element of srt on a new line
            f_raw.write("{}\n".format(i))
            f.write("{} ".format(i['text']))

        f_raw.close()

    text = None
    with open(FILE_VIDEO_SUBTITLES, 'r') as file:
        text = file.read()

    return text


def load_summary_batches():
    with open(FILE_SUMMARY_BATCHES, 'r') as file:
        text = file.read()

    return text


def summarize_transcript_in_batches(text):
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
        or company and in particular Gamestop (ticker: GME). Look for \
        any strategies on how to trade options or mention of the name 'Ryan Cohen'.
        
        Text:
        ```{text_to_edit}```
        """

        # print_response(prompt, text)
        print ("Batch #{}, nr. of tokens: {}, string len: {}".format( count, num_tokens_from_string(prompt), len(prompt) ))
        response = get_completion(prompt)
        summary_batches.append( "- {}\n".format( response ) )

        count = count + 1
        
        # if count > 1:
        #     break

    f_out = open(FILE_SUMMARY_BATCHES, "w")
    for r in summary_batches:
        f_out.write( r )
    f_out.close()

    return summary_batches


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
    
    Use the following format and make sure that maximum line width is no more than 80 characters:
    Title:
    Step 1 here
 
    Summary:
    Step 2 here

    Performance:
    Step 3 here

    Sentiment:
    Step 4 here

    Emotions:
    Step 5 here

    Text:
    ```{text}```
    """
    
    print ("nr. of tokens: {}, string len: {}".format( num_tokens_from_string(prompt), len(prompt) ))
    response = get_completion(prompt)
    f_out = open(FILE_FINAL_SUMMARY, "w")
    f_out.write( response )
    f_out.close()

    print ("Done [filename: {}]!".format(FILE_FINAL_SUMMARY) )

if __name__ == "__main__":
    # with ignoreSSL.no_ssl_verification():
    transcript = download_transcript( '99tkOvP3QAA' )
    summary_batches = summarize_transcript_in_batches( transcript )
    summaries = load_summary_batches()
    create_final_summary( summaries )
