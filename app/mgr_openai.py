import openai
import backoff
import logging
import os
import time
from app import my_helper as HELPER
from openai.error import RateLimitError

AI_API_KEY = None


def init():
    global AI_API_KEY

    AI_API_KEY = os.getenv("AI_API_KEY") or None

    if AI_API_KEY is None:
        raise BaseException("Missing sec configuration (video_summarizer)")
    else:
        openai.api_key = AI_API_KEY

    # configure logging for backoff library
    logging.getLogger("backoff").addHandler(logging.StreamHandler())
    # logging.getLogger('backoff').setLevel(logging.ERROR)


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
        model="gpt-4", messages=messages, temperature=0
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
                model="gpt-4", messages=messages, temperature=0
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
