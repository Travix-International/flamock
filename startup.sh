#!/bin/bash

# PROXY_SCHEME="https";
# PROXY_HOST="www.google.nl";
# PROXY_HEADERS="header1=value1;header2=value2";

echo "Env variables: PROXY_SCHEME=$PROXY_SCHEME, PROXY_HOST=$PROXY_HOST, PROXY_HEADERS=$PROXY_HEADERS";

args="";
if [ -n "$PROXY_HOST" ]; then
    args=$args" --proxy_host $PROXY_HOST";
fi;

if [ -n "$PROXY_SCHEME" ]; then
    args=$args" --proxy_scheme $PROXY_SCHEME";
fi;

if [ -n "$PROXY_HEADERS" ]; then
    args=$args" --proxy_headers $PROXY_HEADERS";
fi;

echo "Starts with args: \"$args\"";


python3 -u flamock.py $args;