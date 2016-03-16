# Sanctuary

![license-MIT-blue](https://img.shields.io/badge/license-MIT-blue.svg)


NOTE: This project is still a work-in-progress.

Sanctuary is a turn-key solution for establishing a production Vault service in the Cloud.

![sanctuary-vpc-diagram](img/sanctuary.png)

## Build

#### Generate AWS Deploy keys
```
./keygen.sh
```

#### Build Container
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
docker run \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"  \
  -i --rm drud/sanctuary [options]
```

This will come complete with some self-signed certs.  If you have your own certs they should be mounted into /etc/certs/{server.key,server.pem}.

This can be done like so:

```
docker run \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"  \
  -i --rm -v /path/to/certs:/etc/certs drud/sanctuary [options]
```

## Interact

```
docker run -it --entrypoint=sh drud/vault
export VAULT_ADDR=http://ip_or_dns_for_vault:8200
vault status -tls-skip-verify
Sealed: true
Key Shares: 5
Key Threshold: 3
Unseal Progress: 0

High-Availability Enabled: true
	Mode: sealed

```
