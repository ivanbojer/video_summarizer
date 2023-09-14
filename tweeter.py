from requests_oauthlib import OAuth1Session
import os
import json
import webbrowser

# Load config values
with open(r'config-tweeter.json') as config_file:
    config_details = json.load(config_file)

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

def authenticate():
    consumer_key = config_details['CONSUMER_KEY'] #os.environ.get("CONSUMER_KEY")
    consumer_secret = config_details['CONSUMER_SECRET'] #os.environ.get("CONSUMER_SECRET")

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


def main():
    oauth = authenticate()
    # Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
    payload = {"text": "Hello world!"}

    json_response = post_tweet( oauth, payload )
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

    #1702139292334936064DJLoky16