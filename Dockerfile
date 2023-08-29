FROM python:3.11.5-alpine

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Instalar FFmpeg en la imagen Alpine
RUN apk update && apk upgrade
RUN apk add --no-cache ffmpeg

CMD [ "python", "src/index.py" ]

