FROM python:3.7.6-alpine

COPY requirements.txt ./app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD . /app
