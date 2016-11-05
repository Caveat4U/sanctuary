FROM ubuntu:trusty

MAINTAINER DRUD DOCKER <docker@drud.io>

# This is only the client version. See the "vault" role in ansible for the server version.
ENV VAULT_VERSION 0.6.2
ENV VAULT_SHA256 91432c812b1264306f8d1ecf7dd237c3d7a8b2b6aebf4f887e487c4e7f69338c
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

WORKDIR /app
ENTRYPOINT ["/usr/bin/python", "sanctuary.py"]
CMD ["create"]