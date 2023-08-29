FROM python:3.11.5-slim
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN apt-get update && apt-get upgrade
RUN apt-get add --no-cache libopus
RUN apt-get add --no-cache ffmpeg


CMD [ "python", "./src/index.py" ]