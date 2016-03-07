FROM ubuntu:trusty

MAINTAINER Drud <erin@newmediadenver.com>

ENV DEBIAN_FRONTEND noninteractive
ENV ANSIBLE_HOST_KEY_CHECKING False

COPY files /

RUN apt-get update -y \
  && apt-get install -y -q build-essential git curl python-setuptools curl unzip python-dev python-pip openssh-client \
  python-yaml python-jinja2 python-httplib2 python-keyczar python-paramiko python-setuptools python-pkg-resources \
  && pip install --upgrade pip \
  && pip install boto ansible click
