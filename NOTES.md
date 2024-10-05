# video_summarizer

## youtube-dl

- https://github.com/ytdl-org/youtube-dl
    sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
    sudo chmod a+rx /usr/local/bin/youtube-dl

- download video and recode into mp4 if not available
    yt-dlp -S res,ext:mp4:m4a --recode "https://www.youtube.com/watch?v=fD3R6ZpHrAQ"

## ffmpeg
- ffmpeg -i input.webm output.mp4


## docker build
- docker build . -t videosummarizer
- docker run -p 127.0.0.1:8080:8080 -t video

## gcloud run
- gcloud config set run/region us-central1
- gcloud builds submit --tag [IMAGE] . 
- gcloud run deploy videosummarizer --image [IMAGE]
-
- gcloud run deploy videosummarizer --source .

## artifactory
- gcloud auth configure-docker us-central1-docker.pkg.dev