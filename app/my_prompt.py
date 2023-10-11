BATCH_PROMPT = """
        You are the stock analyst. I will give you a YouTube video transcript, a text delimited by triple backticks. The narrator's name is Bruce. The transcript contains daily updates on the stock market, advice on option trading strategies, and Bruce's personal stories. You should summarise the text and extract any updates about any particular stock or company mentioned. Pay extra attention to any mention of Gamestop (ticker: GME) and extract any options strategies or advice about trading options. Also, extract any information about 'Ryan Cohen', the CEO of GameStop.
        
        Text:
        ```{}```
        """

# 7 - Provide same steps as JSON string with \
# the following keys: title, long_summary, performance, sentiment, emotions
FINAL_PROMPT = """
    You are the stock analyst. I will give you a YouTube video transcript on multiple lines starting with a dash. All the summaries are part of the same content. The narrator's name is Bruce, and the text is delimited with triple backticks. Perform the following: \
    1 - Create title out of the main focus in the text.
    2 - Summarize the text focusing on any aspects that are relevant to future potential of any company mentioned and especially Gamestop.
    3 - Extract relevant information to any future company performance.
    4 - What is the general sentiment of the text? Format your answer as a list of lower-case words separated by commas.
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
    ```{}```
    """


BATCH_PROMPT_OLD = """
        The text delimited by triple backticks in the context for \
        a Youtube transcript for a narrated video that talks about stock market. \
        The narrator name is Uncle Bruce. The transcript itself contains daily \
        updates on the stock market and Bruce's personal stories. Summarise the text. \
        Extract any updates about any particular stock or any company mentioned and in \
        particular Gamestop (ticker: GME). Look for any options strategies on how to \
        trade options. Extract any information mentioned about 'Ryan Cohen', the CEO of GameStop.
        
        Text:
        ```{}```
        """


# file_chunk_names = [ 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_1.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_2.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_3.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_4.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_5.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_6.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_7.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_8.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_9.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_10.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_11.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_12.mp3',
#                             # 'STOCKS UP IN PRE MARKET IN OVER SOLD ENVIRONMENT STOCK TRADING IN PLAIN ENGLISH WITH UNCLE BRUCE [tEM6rFvfW7g]_chunk_13.mp3']