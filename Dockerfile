FROM python:3.11.5-slim
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN apk update && apk upgrade
RUN apk add --no-cache libopus
RUN apk add --no-cache ffmpeg


CMD [ "python", "./src/index.py" ]