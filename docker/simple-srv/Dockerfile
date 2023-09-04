FROM ubuntu:20.04


RUN apt-get update  && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        net-tools \
        iproute2 \
        iputils-ping \
    && \
    rm -rf /var/lib/apt/lists/*


COPY flaskapp /usr/local/flaskapp

WORKDIR /usr/local/flaskapp

ENV FLASK_APP=main

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT /bin/bash
