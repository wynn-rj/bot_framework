FROM debian:10

RUN apt-get update && apt-get install python3 python3-pip

COPY . /app
RUN mkdir -p /data
RUN mkdir -p /extensions
RUN mkdir -p /config

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["/app/bot_start.py"]
