FROM python:3.7-alpine
LABEL maintainer="trolliama"

# Recommended - Don't Allow the python buffer the outputs
ENV PYTHONUNBUFFERED 1 

COPY ./requirements.txt /requirements.txt
# Dependencies to run postgresql and Pillow
# apk it's the packege install of alpine like: apt
# apk add == apt install
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
# Changes for the app dir
WORKDIR /app 
COPY ./app /app

# Create the images directories
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# By default the docker uses the root user to run the container so..
# Create a user with for just run the application
RUN adduser -D user

# Add permission to the user for the directory
RUN chown -R user:user /vol/
RUN chown -R 755 /vol/web

# Changes to the user
USER user