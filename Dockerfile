############################################################
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

MAINTAINER Igor Rybak "iryb@live.ru"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev git curl wget vim build-essential
RUN git clone https://github.com/baor/flamock.git

WORKDIR /flamock
RUN pip3 install -r requirements.txt

# Expose ports
EXPOSE 1080

ENTRYPOINT ["python3"]
CMD ["-u","flamock.py"]
