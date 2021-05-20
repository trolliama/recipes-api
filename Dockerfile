FROM python:3.7-alpine
LABEL maintainer="trolliama"

# Recommended - Don't Allow the python buffer the outputs
ENV PYTHONUNBUFFERED 1 

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
# Changes for the app dir
WORKDIR /app 
COPY ./app /app

# By default the docker uses the root user to run the container so..
# Create a user with for just run the application
RUN adduser -D user
# Changes to the user
USER user