# VIdeo Summarizer

Video summarizer will sumarize the content of the requested video using default or
user defined prompt and post summary of it as a twitter blog.

This is done in a few steps:
- access user defined video and download close captions
    - if captions are not present (caseof: new video)
    - download video file
    - extract audio using ffmpeg package
- send close captions to openai together with user prompt
- send part of the return to the twitter accouns as a blog post
    - twitter api as of today does not allow for long text so we 
        have to split text in a thread of a user-defined size.
        Hopefully this is not needed in the future or with 
        paid version of twitter subscription.

## Deployment

I currently deploy this code in cloud run. Appropriate docker filer is present 
that will be used to build image that then can be pushed to the google run
- see [NOTES.md] (./NOTES.md) for a cheat sheet

## Configuration

Make sure you modify following files for your usage

- .env
- config.json

## How to run

- see [entrypoint.sh] (./entrypoint.sh) for local run
- cloud run [NOTES.md] (./NOTES.md)
- docket [NOTES.md] (./NOTES.md)