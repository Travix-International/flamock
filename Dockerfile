############################################################
# Dockerfile to build Python WSGI Application Containers
############################################################

FROM travix/base-debian:latest

MAINTAINER Travix
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    python3-dev \
    python3-pip \
    vim \
    wget \
&& rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/Travix-International/flamock.git

WORKDIR /flamock
RUN pip3 install -r requirements.txt

# Expose ports
EXPOSE 1080

# Setup for pipeline
#CMD PROXY_SCHEME="https"; \
#    PROXY_HOST="www.google.nl"; \
#    PROXY_HEADERS="header1=value1;header2=value2"; \
CMD echo "Env variables: PROXY_SCHEME=$PROXY_SCHEME, PROXY_HOST=$PROXY_HOST, PROXY_HEADERS=$PROXY_HEADERS"; \
    args=""; \
    if [ -n "$PROXY_HOST" ]; then \
        args=$args" --proxy_host $PROXY_HOST"; \
    fi; \
    if [ -n "$PROXY_SCHEME" ]; then \
        args=$args" --proxy_scheme $PROXY_SCHEME"; \
    fi; \
    if [ -n "$PROXY_HEADERS" ]; then \
        args=$args" --proxy_headers $PROXY_HEADERS"; \
    fi; \
    echo "Starts with args: \"$args\""; \
    python3 -u flamock.py $args; \