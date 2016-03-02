# Sanctuary

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