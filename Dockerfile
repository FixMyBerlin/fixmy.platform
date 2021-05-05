FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update; apt-get --assume-yes --auto-remove install \
    apt-transport-https \
    binutils \
    curl \
    gdal-bin \
    gettext \
    libproj-dev \
    locales \
    postgresql-client \
    unzip \
    less \
    vim

RUN rm -rf /var/lib/apt/lists/*
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code/
