import openai
import backoff
import logging
import os
import time
import json
from app import my_helper as HELPER
from openai.error import RateLimitError

# Load config values
with open(r"config.json") as config_file:
    config_details2 = json.load(config_file)

AI_API_KEY = None


def init():
    global AI_API_KEY, GPT_MODEL

    AI_API_KEY = os.getenv("AI_API_KEY") or None
    GPT_MODEL = config_details2["OA_CHAT_GPT_MODEL"]

    if AI_API_KEY is None:
        raise BaseException("Missing sec configuration (video_summarizer)")
    else:
        openai.api_key = AI_API_KEY

    # configure logging for backoff library
    logging.getLogger("backoff").addHandler(logging.StreamHandler())
    logging.getLogger('backoff').setLevel(logging.INFO)


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def completions_with_backoff(system_prompt, user_prompt):
    if not openai.api_key:
        init()

    user_prompt = HELPER.FIX_TEXT(user_prompt)
    system_prompt = HELPER.FIX_TEXT(system_prompt)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL, messages=messages, temperature=0
    )

    return response.choices[0].message["content"]


# Define a function that adds a delay to a Completion API call
def delayed_completion(
    system_prompt, user_prompt, delay_in_seconds: float = 7, retries: int = 10
):
    """Delay a completion by a specified amount of time."""

    if not openai.api_key:
        init()

    user_prompt = HELPER.FIX_TEXT(user_prompt)
    # Call the Completion API and return the result
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = None
    retry_attempts = 1
    while response is None:
        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL, messages=messages, temperature=0
            )
        except RateLimitError as rate_err:
            print(
                "Sleeping for {}s, retry attempt #{}, error_msg: {}".format(
                    delay_in_seconds, retry_attempts, rate_err.user_message
                )
            )
            time.sleep(delay_in_seconds)
            response = None
            retry_attempts = retry_attempts + 1
            if retry_attempts >= retries:
                raise BaseException("Exceeded number of retries [{}]".format(retries))

    return response.choices[0].message["content"]
