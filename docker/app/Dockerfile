FROM python:3.9

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update; apt-get --assume-yes --auto-remove install \
    binutils \
    curl \
    gdal-bin \
    gettext \
    less \
    libproj-dev \
    locales \
    postgresql-client \
    unzip \
    vim && rm -rf /var/lib/apt/lists/*
WORKDIR /code
ADD requirements.txt /code
RUN pip install --no-cache-dir -r requirements.txt
ADD . /code/
RUN python manage.py compilemessages
COPY ./docker/app/docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 8000
CMD ["--bind", "0.0.0.0", "--timeout", "180", "fixmydjango.wsgi"]
