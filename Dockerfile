FROM ubuntu:trusty

MAINTAINER DRUD DOCKER <docker@drud.io>

ENV VAULT_VERSION 0.5.1
ENV VAULT_SHA256 7319b6514cb5ca735d9886d7b7e1ed8730ee38b238bb1626564436b824206d12
ENV DEBIAN_FRONTEND noninteractive
ENV ANSIBLE_HOST_KEY_CHECKING False
ENV ANSIBLE_FORCE_COLOR True

COPY apt-requirements.txt /
COPY pip-requirements.txt /
ADD https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip /tmp/vault.zip

RUN  apt-get update -y \
  && apt-get install -y -q $(cat /apt-requirements.txt) \
  && pip install --upgrade pip \
  && pip install -r /pip-requirements.txt \
  && echo "${VAULT_SHA256} */tmp/vault.zip" | sha256sum -c - \
  && cd /bin && unzip /tmp/vault.zip && chmod +x /bin/vault && rm /tmp/vault.zip

COPY files /

ENTRYPOINT ["/usr/bin/python", "/app/sanctuary.py"]
CMD ["create"]
