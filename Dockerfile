# This image is intended for the git CI

FROM ubuntu:16.04
LABEL maintainer "frank@sauerburger.com"


RUN apt-get update && apt-get install -y  \
  python3 python3-setuptools git recode\
  && rm -rf /var/lib/apt/lists/*

