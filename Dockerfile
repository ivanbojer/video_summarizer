# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim
# pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local mainly static code to the container image.
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
# credentials (need to address this)
COPY ./config.json /app/config.json
# Install production dependencies 1
RUN apt-get update && apt-get install -y ffmpeg
# Install production dependencies 2
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
# RUN pip install -r requirements.txt
# dummy data for testing
RUN mkdir -p /app/temp_data/
COPY ./temp_data/video_FINAL_SUMMARY.txt /app/temp_data/

COPY ./app /app/app
# run the app
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]
