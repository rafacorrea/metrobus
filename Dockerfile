FROM python:3.7.6-alpine

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev geos-dev

COPY requirements.txt ./app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD . /app
