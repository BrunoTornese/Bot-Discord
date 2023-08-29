FROM python:3.11.5-alpine

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN apk update && apk upgrade
RUN apk add --no-cache libopus ffmpeg

CMD [ "python", "./src/index.py" ]