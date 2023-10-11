# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim
# pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
# Install production dependencies.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# RUN pip install -r requirements.txt

COPY ./temp_data/video_FINAL_SUMMARY.txt /code/temp_data/video_FINAL_SUMMARY.txt
COPY ./config.json /code/config.json
COPY ./app /code/app



CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]

