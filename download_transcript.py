from youtube_transcript_api import YouTubeTranscriptApi
import ignoreSSL

import openai
import os
import json

# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

openai.api_key = config_details['OPENAI_API_KEY']
openai.api_base = config_details['OPENAI_API_BASE']
openai.api_version = config_details['OPENAI_API_VERSION']
openai.api_type = config_details['OPENAI_API_TYPE']


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output,
        engine=config_details['CHAT_GPT_MODEL']
    )
    return response.choices[0].message["content"]


def print_response(prompt, text=None):
    response = get_completion(prompt)
    print(response)


def download_transcript(): 
    # assigning srt variable with the list
    # of dictionaries obtained by the get_transcript() function
    srt = YouTubeTranscriptApi.get_transcript("NhqYqVZLC1A")
    
    # prints the result
    # print(srt)

    # creating or overwriting a file "subtitles.txt" with
    # the info inside the context manager
    with open("subtitles.txt", "w") as f:
        f_raw = open("subtitles_raw.txt", "w")
        # iterating through each element of list srt
        for i in srt:
            # writing each element of srt on a new line
            f.write("{}\n".format(i))
            f_raw.write("{}\n".format(i['text']))

        f_raw.close()


def summarize_transcript():
    text = None
    with open('subtitles_raw.txt', 'r') as file:
        text = file.read().replace('\n', '')

    prompt = f"""
    Perform the following actions:
    1 - Summarize the text delimited by triple backticks \ 
    into a single sentence.
    2 - Summarize the text delimited by triple backticks, \
    in at most 30 words and focusing on any aspects that \
    are relevant to future company potential.
    3 - Extract relevant information to future company performance.
    4 - What is the general sentiment of the text, \
    which is delimited with triple backticks?
    5 - Identify a list of emotions in the text \
    which is delimited with triple backticks? \
    Format your answer as a list of \
    lower-case words separated by commas.
     
    Use the following format:
    Summary:
    '''
    Step 1 here
    '''
    Long summary:
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

    Text:
    ```{text}```
    """

    print_response(prompt, text)

if __name__ == "__main__":
    with ignoreSSL.no_ssl_verification():
        download_transcript()
        summarize_transcript()