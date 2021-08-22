FROM python:3.9-slim

WORKDIR /usr/app

COPY requirements.txt .

RUN set -ex && \
  pip3 --no-cache-dir install -r requirements.txt

ADD . .

ENTRYPOINT ["python3", "app.py"]
