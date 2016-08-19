#!/bin/bash

# PROXY_SCHEME="https";
# PROXY_HOST="www.google.nl";
# PROXY_HEADERS="header1=value1;header2=value2";
# PORTS="8801 8802 8805"

echo "Env variables: PROXY_SCHEME=$PROXY_SCHEME, PROXY_HOST=$PROXY_HOST, PROXY_HEADERS=$PROXY_HEADERS, PORTS=$PORTS"

args=""
if [ -n "$PROXY_HOST" ]; then
    args=$args" --proxy_host $PROXY_HOST"
fi

if [ -n "$PROXY_SCHEME" ]; then
    args=$args" --proxy_scheme $PROXY_SCHEME"
fi

if [ -n "$PROXY_HEADERS" ]; then
    args=$args" --proxy_headers $PROXY_HEADERS"
fi

if [ -n "$PORTS" ]; then
    for port in $PORTS; do
        port=" --port "$port
        echo "Starts with args: \"$args$port\""
        python3 -u flamock.py $args$port &
    done
else
    echo "Starts with args: \"$args\""
    python3 -u flamock.py $args
fi