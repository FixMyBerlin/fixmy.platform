FROM python:3.6

MAINTAINER Boris Hekele <hekele@parliamentwatch.org>

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
    unzip

RUN rm -rf /var/lib/apt/lists/*
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code/
