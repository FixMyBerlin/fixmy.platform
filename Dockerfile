FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV LANG en_US.utf8

# Add PostgreSQL repository to be able to install `postgresql-client-13`
# c.f https://wiki.postgresql.org/wiki/Apt
RUN apt-get update; \
    apt-get --assume-yes --auto-remove install curl ca-certificates gnupg2 lsb-release; \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -; \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |tee  /etc/apt/sources.list.d/pgdg.list;

RUN apt-get update; apt-get --assume-yes --auto-remove install \
    apt-transport-https \
    binutils \
    curl \
    gdal-bin \
    gettext \
    libproj-dev \
    locales \
    postgresql-client-13 \
    unzip \
    less \
    vim

RUN rm -rf /var/lib/apt/lists/*
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code/
