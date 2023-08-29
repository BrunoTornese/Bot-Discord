FROM python:3.11.5

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

CMD [ "python", "index.py" ]
