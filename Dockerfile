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
# ENV MOCK_ADD_EXPECTATION_PATH mock_admin/add_expectation
# ENV FWD_SCHEME https
# ENV FWD_HOST www.google.nl

CMD if [ -n "$FWD_SCHEME" ] && [ -n "$FWD_HOST" ] && [ -n "$MOCK_ADD_EXPECTATION_PATH" ]; then \
        curl \
            -H "Content-Type: application/json" \
            -X POST \
            -d '{ "key": "fwd", "forward": { "scheme": "${FWD_SCHEME}", "host": "${FWD_HOST}" }, "unlimited": true, "priority": 0 }' \
            http://0.0.0.0:1080/${MOCK_ADD_EXPECTATION_PATH}; \
    fi; \
    python3 -u flamock.py;