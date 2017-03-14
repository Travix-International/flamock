#!/bin/bash

# PROXY_SCHEME="https";
# PROXY_HOST="www.google.nl";
# PROXY_HEADERS="header1=value1;header2=value2";
# PORTS="8801 8802 8805"
# EXPECTATIONS="[{\"key\":\"fwd8801\",\"request\":{\"headers\":{\"X-Incoming-Port\":\"8801\"}},\"forward\":{\"scheme\":\"http\",\"host\":\"google.com:8801\"},\"priority\":0},{\"key\":\"fwd8802\",\"request\":{\"headers\":{\"X-Incoming-Port\":\"8802\"}},\"forward\":{\"scheme\":\"http\",\"host\":\"google.com:8802\"},\"priority\":0},{\"key\":\"fwd8805\",\"request\":{\"headers\":{\"X-Incoming-Port\":\"8805\"}},\"forward\":{\"scheme\":\"http\",\"host\":\"google.com:8805\"},\"priority\":0}]"

echo "Env variables: PROXY_SCHEME=$PROXY_SCHEME, PROXY_HOST=$PROXY_HOST, PROXY_HEADERS=$PROXY_HEADERS, PORTS=$PORTS, EXPECTATIONS=$EXPECTATIONS"

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

if [ -n "$EXPECTATIONS" ]; then
    args=$args" --expectations $EXPECTATIONS"
fi

if [ -n "$WHITE_LIST" ]; then
    args=$args" --whitelist $WHITE_LIST"
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