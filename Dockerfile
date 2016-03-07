FROM ubuntu:trusty

MAINTAINER Drud <erin@newmediadenver.com>

ENV DEBIAN_FRONTEND noninteractive
ENV ANSIBLE_HOST_KEY_CHECKING False

COPY files /

RUN apt-get update -y \
  && apt-get install -y -q $(cat /apt-requirements.txt) \
  && pip install --upgrade pip \
  && pip install $(cat /pip-requirements.txt)

