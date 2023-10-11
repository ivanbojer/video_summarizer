# video_summarizer

## youtube-dl

- https://github.com/ytdl-org/youtube-dl
    sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
    sudo chmod a+rx /usr/local/bin/youtube-dl


## docker build
- docker build . -t videosummarizer
- docker run -p 127.0.0.1:8080:8080 -t video

## gcloud run
- gcloud config set run/region us-central1
- gcloud builds submit --tag [IMAGE] . 
- gcloud run deploy videosummarizer --image [IMAGE]

## artifactory
- gcloud auth configure-docker us-central1-docker.pkg.dev