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
# ENV PROXY_SCHEME https
# ENV PROXY_HOST www.google.nl

CMD if [ -n "$PROXY_HOST" ] && [ -n "$PROXY_SCHEME" ]; then \
        python3 -u flamock.py --proxy_scheme $PROXY_SCHEME --proxy_host $PROXY_HOST; \
    else \
        python3 -u flamock.py; \
    fi;