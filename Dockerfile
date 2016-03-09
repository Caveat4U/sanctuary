FROM ubuntu:trusty

MAINTAINER DRUD DOCKER <docker@drud.io>

ENV DEBIAN_FRONTEND noninteractive
ENV ANSIBLE_HOST_KEY_CHECKING False
ENV ANSIBLE_FORCE_COLOR True

COPY files/apt-requirements.txt /
COPY files/pip-requirements.txt /

RUN apt-get update -y \
  && apt-get install -y -q $(cat /apt-requirements.txt) \
  && pip install --upgrade pip \
  && pip install -r /pip-requirements.txt

COPY files /

ENTRYPOINT ["/usr/bin/python", "/app/sanctuary.py"]
CMD ["create"]
