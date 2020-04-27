FROM debian:10

RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip

COPY . /app

RUN mkdir -p /data /extensions /config

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["python3", "/app/bot_start.py"]
