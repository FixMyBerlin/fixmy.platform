FROM python:3.8

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

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
    less \
    libproj-dev \
    locales \
    postgresql-client-13 \
    unzip \
    vim && rm -rf /var/lib/apt/lists/*
WORKDIR /code
ADD requirements.txt /code
RUN pip install --no-cache-dir -r requirements.txt
ADD . /code/
COPY ./docker/app/docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 8000
CMD ["--bind", "0.0.0.0", "fixmydjango.wsgi"]
