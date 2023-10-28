from requests_oauthlib import OAuth1Session
import os
import json
import webbrowser
from app import ignoreSSL
from app import logger


class TweeterMgr:
    # In your terminal please set your environment variables by running the following lines of code.
    # export 'CONSUMER_KEY'='<your_consumer_key>'
    # export 'CONSUMER_SECRET'='<your_consumer_secret>'

    MAX_TWEET_SIZE_CHARACTERS = 10000
    FOOTER = " #GME #Gamestop #Superstonk"
    HEADER = " Uncle Bruce's Wisdom"
    TW_THREAD_COUNT_CHARS = len("xx/xx ")
    config_details2 = None

    def __init__(
        self,
        max_tweeet_size_characters=MAX_TWEET_SIZE_CHARACTERS,
        footer=FOOTER,
        header=HEADER,
        tw_thread_count_chars=TW_THREAD_COUNT_CHARS,
    ):
        self.max_tweeet_size_characters = max_tweeet_size_characters
        self.footer = footer
        self.header = header
        self.tw_thread_count_chars = tw_thread_count_chars

        # Load config values
        with open(r"config.json") as config_file:
            self.config_details2 = json.load(config_file)

        self.__authenticate()

    def __authenticate(self):
        consumer_key = os.getenv("TW_CONSUMER_KEY")  # os.environ.get("CONSUMER_KEY")
        consumer_secret = os.getenv(
            "TW_CONSUMER_SECRET"
        )  # os.environ.get("CONSUMER_SECRET")

        if not os.path.exists("token.json"):
            # Get request token
            request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
            oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

            try:
                fetch_response = oauth.fetch_request_token(request_token_url)
            except ValueError:
                logger.logger.error(
                    "There may have been an issue with the consumer_key or consumer_secret you entered."
                )

            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            logger.logger.info("Got OAuth token: %s" % resource_owner_key)

            # Get authorization
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = oauth.authorization_url(base_authorization_url)
            logger.logger.info("Please go here and authorize: %s" % authorization_url)
            webbrowser.open(authorization_url)
            verifier = input("Paste the PIN here: ")

            # Get the access token
            access_token_url = "https://api.twitter.com/oauth/access_token"
            oauth = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                verifier=verifier,
            )
            oauth_tokens = oauth.fetch_access_token(access_token_url)

            with open("token.json", "w") as tok_file:
                tok_file.write(json.dumps(oauth_tokens))
        else:
            with open("token.json", "r") as tok_file:
                oauth_tokens = json.load(tok_file)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        self.oauth = oauth

    def post_tweet(self, text, header=None, fake_run=False):
        if not self.oauth:
            raise Exception("Not authenticated")

        if header:
            self.header = header

        if len(text) > self.max_tweeet_size_characters - len(self.footer) - len(header):
            return self.__post_tweet_in_chunks(text, fake_run)
        else:
            payload = {}
            payload["reply_settings"] = "mentionedUsers"
            payload["text"] = "{}\n{}\n{}".format(self.header, text, self.footer)
            return self.__post_tweet(payload, fake_run)

    def __post_tweet(self, payload, fake_run=False):
        json_response = None
        if not fake_run:
            # Making the request
            response = self.oauth.post("https://api.twitter.com/2/tweets", json=payload)

            if response.status_code != 201:
                raise Exception(
                    "Request returned an error: {} {}".format(
                        response.status_code, response.text
                    )
                )

            logger.logger.info("Response code: {}".format(response.status_code))

            # Saving the response as JSON
            json_response = response.json()

        logger.logger.info("Payload:{}".format(payload["text"]))
        return json_response

    def __split_text_in_chunks(self, text):
        # text = text.replace('\n', '')

        # TW_THREAD_COUNT_CHARS is for "1/2"
        # we add another 3 spacers for line breaks, etc...
        max_chunk_chars = (
            self.max_tweeet_size_characters
            - len(self.footer)
            - self.tw_thread_count_chars
            - len(self.header)
            - 3
        )

        txt_chunks = []
        count = 1
        start = 0
        end = min(max_chunk_chars, len(text))
        while end < (len(text) - 1):
            count = count + 1
            end = min(start + max_chunk_chars, len(text) - 1)

            while text[end] != ".":
                # logger.logger.info('start:{} end:{} c:{}'.format( start, end, text[end]) )
                # logger.logger.info(text[start:end])
                end = end - 1

                # in case that the whole sentence is greater than
                # max_chunk_chars and there is not '.' to be found
                # just use it as-is
                if end == start:
                    end = min(start + max_chunk_chars, len(text) - 1)
                    break

            end = end + 1

            # sometime we just end up with white space and we do not need to tweet that
            if text[start:end].strip() != "":
                txt_chunks.append("{}\n{}".format(text[start:end], self.footer).strip())

            start = end

        # figure how many chunks we have for the output
        total_chunks = len(txt_chunks)

        # add the header (ex. 1/5, 2/5, 10/20, ..., )
        for idx, chunk in enumerate(txt_chunks):
            if idx == 0:
                txt_chunks[idx] = "{}/{} {}\n{}".format(
                    idx + 1, total_chunks, self.header, chunk
                )
            else:
                txt_chunks[idx] = "{}/{} {}".format(idx + 1, total_chunks, chunk)

        return txt_chunks

    def __post_tweet_in_chunks(self, text, fake_run=False):
        text_chunks = self.__split_text_in_chunks(text)

        json_response = None
        for idx, chunk in enumerate(text_chunks):
            if idx == 0:
                payload = {"text": chunk, "reply_settings": "mentionedUsers"}
            else:
                payload = {
                    "text": chunk,
                    "reply": {"in_reply_to_tweet_id": json_response["data"]["id"]},
                }

            logger.logger.info("{}".format(payload["text"]))

            if not fake_run:
                json_response = self.__post_tweet(payload)
            else:
                json_response = {"data": {"id": "FAKE RUN"}}

    def get_all_tweets(self):
        if not self.oauth:
            raise Exception("Not authenticated")

        params = {"ids": "1703277554902441984", "tweet.fields": "created_at"}
        # Making the request
        response = self.oauth.get("https://api.twitter.com/2/tweets", params=params)

        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        logger.logger.info("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()

        return json_response

    def user_lookup(self):
        if not self.oauth:
            raise Exception("Not authenticated")

        # User fields are adjustable, options include:
        # created_at, description, entities, id, location, name,
        # pinned_tweet_id, profile_image_url, protected,
        # public_metrics, url, username, verified, and withheld
        fields = "created_at,description"
        params = {"user.fields": fields}

        # Making the request
        response = self.oauth.get("https://api.twitter.com/2/users/me", params=params)

        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        logger.logger.info("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()

        return json_response

    def test(self):
        text = """
    Uncle Bruce, a seasoned figure in the world of finance and trading, has left an indelible mark on my journey as an investor. I first came across him several years ago when my curiosity was piqued by the GameStop (GME) frenzy. Little did I know that this initial interest would lead me to a wealth of knowledge and wisdom.
    Initially, Uncle Bruce's focus was on deciphering the enigma that was GME, shedding light on its intricacies and market dynamics. However, as time flowed like a steady river, I began to realize that Uncle Bruce's expertise extended far beyond a single stock. His teachings transcended the realm of GameStop, delving into the world of options trading.
    It was under Uncle Bruce's guidance that I honed my skills and became a more successful trader. His unique approach and insightful strategies transformed my understanding of the financial markets. Although GME may not be at the forefront of his discussions as it once was, Uncle Bruce's stories continue to serve as a wellspring of profound insights.
    Uncle Bruce's background as a former broker adds a layer of authenticity to his teachings. His experiences in the brokerage industry provide a solid foundation for the wisdom he imparts to his followers.
    In summary, Uncle Bruce's journey from unraveling the mysteries of GME to becoming a beacon of knowledge in options trading is a testament to his dedication and expertise. His life story, filled with valuable lessons and profound insights, continues to inspire and guide those who seek to navigate the complex world of finance.
    """

        # send tweet (chunk if needed)
        # post_tweet( text )

        import video_summarizer

        response = ""
        with open(video_summarizer.FILE_FINAL_SUMMARY, "r") as file:
            response = file.read()

        title, text = video_summarizer.extract_blog_section(response)

        self.post_tweet(text, title, True)

        # txt_chunks = self.__split_text_in_chunks(text)
        # for idx,c in enumerate(txt_chunks):
        #     logger.logger.info('chunk #{}. len:{}'.format( idx, len(c)))

        # for idx,c in enumerate(txt_chunks):
        #     logger.logger.info( c )


if __name__ == "__main__":
    with ignoreSSL.no_ssl_verification():
        tw = TweeterMgr()
        tw.test()
