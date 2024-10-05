# VIdeo Summarizer

Video Summarizer – leveraging the power of Generative AI to transform how we consume video content!

Video summarizer will sumarize the content of the requested video using default or
user defined prompt and post summary of it as a twitter blog.

With video content on the rise, it’s often challenging to keep up. My Python-based **Video Summarizer** uses **AI** to automatically generate insightful summaries from any video, whether it has captions or not. Here’s how it works:

- Captions or No Captions? If captions are available, it uses those to craft the summary. If not, the tool extracts audio from the video using ffmpeg, and converts it to text.
- Generative AI Magic: The extracted text (or captions) is fed into OpenAI’s model, which generates a summary based on either a default or user-defined prompt.
- Sharing Insights on Twitter: The summary is then posted as a series of concise Twitter threads, making it easier to share knowledge across platforms. While Twitter has text limitations, the tool automatically splits long content into manageable threads.

By combining Generative AI and automation, this project helps unlock the essence of video content, making it more accessible and shareable in today’s fast-paced digital world. Imagine the possibilities for researchers, content creators, and anyone who wants to stay informed without watching long videos!


## Deployment

I currently deploy this code in cloud run. Appropriate docker filer is present 
that will be used to build image that then can be pushed to the google run
- see [NOTES.md](./NOTES.md) for a cheat sheet

## Configuration

Make sure you modify following files for your usage

- .env
- config.json

## How to run

- see [entrypoint.sh](./entrypoint.sh) for local run
- cloud run [NOTES.md](./NOTES.md)
- docket [NOTES.md](./NOTES.md)
