FROM python:3.11.5-slim-bullseye

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./src/index.py" ]
