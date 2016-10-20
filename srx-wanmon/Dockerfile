
FROM ubuntu:trusty

MAINTAINER ndavey@packetpusher.ca

RUN apt-get update && apt-get install -y \
  python2.7 \
  python-pip \
  python2.7-dev \
  gunicorn \
  python-lxml \
  libffi-dev \
  libssl-dev \
  libxslt1-dev \
  git

RUN pip install junos-eznc flask

RUN git clone https://github.com/ndavey/srx-wanmon

EXPOSE 8000

CMD python /srx-wanmon/app.py
