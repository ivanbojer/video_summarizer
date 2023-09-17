from requests_oauthlib import OAuth1Session
import os
import json
import webbrowser
import datetime
import ignoreSSL

# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

def authenticate():
    consumer_key = config_details['TW_CONSUMER_KEY'] #os.environ.get("CONSUMER_KEY")
    consumer_secret = config_details['TW_CONSUMER_SECRET'] #os.environ.get("CONSUMER_SECRET")

    if not os.path.exists('token.json'):
        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        webbrowser.open( authorization_url )
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

        with open('token.json', 'w') as tok_file:
            tok_file.write( json.dumps(oauth_tokens) )
    else:
        with open('token.json', 'r') as tok_file:
            oauth_tokens = json.load( tok_file )

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    return oauth


def post_tweet(oauth, payload):
    if not oauth:
        raise Exception(
            "Not authenticated"
        )
    
    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()

    return json_response


def post_tweet_in_chunks( oauth, text):
    text = text.replace('\n', '')
    MAX_CHUNK = 240
    total_chunks = round(len(text) / MAX_CHUNK )

    start = 0
    count = 1
    end = min(MAX_CHUNK, len(text) )
    print('{}/{}\n{}\n'.format( count, total_chunks, text[start:end]) )

    # payload = { "text": '{}/{}\n{}\n'.format( count, total, text[start:end]),
    #            "reply_settings": "mentionedUsers"
    #           }
    # json_response = post_tweet( oauth, payload )

    if len(text) > MAX_CHUNK:
        start = MAX_CHUNK
        while end < (len(text)-1):
            count = count + 1
            end = min(start + MAX_CHUNK, len(text)-1)

            while text[end] != '.':
                end = end -1

            end = end + 1

            # payload = { "text": '{}/{}\n{}\n'.format( count, total, text[start:end]),
            #    "reply": { 
            #         "in_reply_to_tweet_id": json_response['data']['id']
            #              }
            #   }
            # json_response = post_tweet( oauth, payload )
            print('{}/{}\n{}\n'.format( count, total_chunks, text[start:end]) )

            start = end

    # payload = { "text": body,
    #            "reply_settings": "mentionedUsers"
    #           }
    # json_response = post_tweet( oauth, payload )

       


        #         if len(text) > MAX_CHUNK:
        # start = MAX_CHUNK
        # end = start+MAX_CHUNK
        # for indx, text_chunk in enumerate(range(MAX_CHUNK, len(text), MAX_CHUNK)):
        #     start = text_chunk
        #     end = min(text_chunk+MAX_CHUNK, len(text))
        #     print('Batch #{}\n{}\n'.format( indx, text[start:end]) )
    
def get_all_tweets( oauth ):
    if not oauth:
        raise Exception(
            "Not authenticated"
        )
    
    params = {"ids": "1703277554902441984", "tweet.fields": "created_at"}
    # Making the request
    response = oauth.get(
        "https://api.twitter.com/2/tweets",
        params = params
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()

    return json_response


def user_lookup( oauth ):
    if not oauth:
        raise Exception(
            "Not authenticated"
        )
    
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    fields = "created_at,description"
    params = {"user.fields": fields}

    # Making the request
    response = oauth.get(
        "https://api.twitter.com/2/users/me",
        params = params
    )

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()

    return json_response
def main():
    # auth first
    oauth = authenticate()

    # Be sure to add replace the text of the with the text you wish to Tweet. 
    # You can also add parameters to post polls, quote Tweets, Tweet with reply 
    # settings, and Tweet to Super Followers in addition to other features.
    # payload = { "text": "1/2 Hello world! [{}]".format( datetime.datetime.today().today().isoformat() ),
    #            "reply_settings": "mentionedUsers"
    #           }
    # json_response = post_tweet( oauth, payload )

    # json_response = get_all_tweets( oauth )

    # json_response = user_lookup( oauth )

    # print out the return response
    # print(json.dumps(json_response, indent=4, sort_keys=True))

    # payload = { "text": "Hello world AGAIN! [{}]".format( datetime.datetime.today().today().isoformat() ),
    #            "reply_settings": "mentionedUsers",
    #            "quote_tweet_id": json_response['data']['id']
    # }
    # json_response = post_tweet( oauth, payload )

    # payload = { "text": "2/2 Hello world! [{}]".format( datetime.datetime.today().today().isoformat() ),
    #             "reply": { 
    #                 "in_reply_to_tweet_id": json_response['data']['id']
    #                      }
    #           }
    # json_response = post_tweet( oauth, payload )
    # print out the return response
    # print(json.dumps(json_response, indent=4, sort_keys=True))

    text = '''
Uncle Bruce, a seasoned figure in the world of finance and trading, has left an indelible mark on my journey as an investor. I first came across him several years ago when my curiosity was piqued by the GameStop (GME) frenzy. Little did I know that this initial interest would lead me to a wealth of knowledge and wisdom.

Initially, Uncle Bruce's focus was on deciphering the enigma that was GME, shedding light on its intricacies and market dynamics. However, as time flowed like a steady river, I began to realize that Uncle Bruce's expertise extended far beyond a single stock. His teachings transcended the realm of GameStop, delving into the world of options trading.

It was under Uncle Bruce's guidance that I honed my skills and became a more successful trader. His unique approach and insightful strategies transformed my understanding of the financial markets. Although GME may not be at the forefront of his discussions as it once was, Uncle Bruce's stories continue to serve as a wellspring of profound insights.

Uncle Bruce's background as a former broker adds a layer of authenticity to his teachings. His experiences in the brokerage industry provide a solid foundation for the wisdom he imparts to his followers.

In summary, Uncle Bruce's journey from unraveling the mysteries of GME to becoming a beacon of knowledge in options trading is a testament to his dedication and expertise. His life story, filled with valuable lessons and profound insights, continues to inspire and guide those who seek to navigate the complex world of finance.
'''

    post_tweet_in_chunks( oauth, text )


if __name__ == "__main__":
    with ignoreSSL.no_ssl_verification():
        main()