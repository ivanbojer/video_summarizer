import openai
import os
import json

# Load config values
with open(r'config-openai.json') as config_file:
    config_details = json.load(config_file)

openai.api_key = config_details['OPENAI_API_KEY']
# openai.api_base = config_details['OPENAI_API_BASE']
# openai.api_version = config_details['OPENAI_API_VERSION']
# openai.api_type = config_details['OPENAI_API_TYPE']


import os
import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output,
        max_tokens=256
        # engine=config_details['CHAT_GPT_MODEL']
    )
    return response.choices[0].message["content"]


def print_response(prompt, text=None):
    response = get_completion(prompt)
    print(response)

prompt = f"""
What day is today?
"""

# print_response( prompt )

# import scrapetube

# videos = scrapetube.get_channel("UCYNM_dInWi_glMZT3gxqxPQ")

# for video in videos:
#     print(video['videoId'])

f = open('response0.txt', 'r')
text = f.read().replace('\n', '')
print ( text )