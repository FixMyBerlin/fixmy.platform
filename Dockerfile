FROM python:3.6

MAINTAINER Boris Hekele <hekele@parliamentwatch.org>

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update ; apt-get --assume-yes --auto-remove install unzip curl locales binutils apt-transport-https libproj-dev gdal-bin

RUN rm -rf /var/lib/apt/lists/*

# RUN wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
# RUN tar -xjf geos-3.4.2.tar.bz2
# RUN cd geos-3.4.2; ./configure; make; make install

# RUN wget http://download.osgeo.org/gdal/1.11.0/gdal-1.11.0.tar.gz
# RUN tar -xzf gdal-1.11.0.tar.gz
# RUN cd gdal-1.11.0; ./configure; make; make install

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code/
