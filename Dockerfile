FROM python:3.7-alpine
LABEL maintainer="trolliama"

# Recommended - Don't Allow the python buffer the outputs
ENV PYTHONUNBUFFERED 1 

COPY ./requirements.txt /requirements.txt
# Dependencies to run postgresql
# apk it's the packege install of alpine like: apt
# apk add == apt install
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
# Changes for the app dir
WORKDIR /app 
COPY ./app /app

# By default the docker uses the root user to run the container so..
# Create a user with for just run the application
RUN adduser -D user
# Changes to the user
USER user