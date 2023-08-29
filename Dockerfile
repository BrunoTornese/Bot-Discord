FROM python:3.11.5-alpine

WORKDIR /app

COPY . /app

RUN apk add --no-cache ffmpeg
RUN pip install -r requirements.txt

CMD [ "python", "src/index.py" ]
