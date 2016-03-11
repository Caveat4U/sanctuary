#!/bin/bash
KEYNAME="keys/deployer.key"

if [ ! -d "keys" ]; then
  mkdir keys
fi

if [ ! -f $KEYNAME ]; then
  ssh-keygen -t rsa -b 4096 -f keys/deployer.key -N ''
fi
