# Sanctuary

![license-MIT-blue](https://img.shields.io/badge/license-MIT-blue.svg)



NOTE: This project is still a work-in-progress.

Sanctuary is a turn-key solution for establishing a production Vault service in the Cloud.

## Build

```
docker build -t drud/sancutary .
```

## Test

```
docker run --rm drud/sanctuary ansible -i 127.0.0.1, -m ping all --connection=local
127.0.0.1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## Run

```
docker run --rm \
-e AWS_ACCESS_KEY_ID="aws access key" \
-e AWS_SECRET_ACCESS_KEY="aws secret key" \
drud/sanctuary python sanctuary.py [options]
```
