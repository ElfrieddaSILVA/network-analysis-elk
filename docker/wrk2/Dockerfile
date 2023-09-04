FROM ubuntu:20.04


RUN apt-get update  && \
    apt-get install -y --no-install-recommends \
        git \
        make \
        gcc \
        curl \
        libghc-zlib-dev \
        net-tools \
        iproute2 \
        iputils-ping \
        libc6-dev \
        ca-certificates \
    && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /tmp

RUN curl -L --output openssl.tar.gz https://ftp.openssl.org/source/old/1.1.1/openssl-1.1.1i.tar.gz  && \
    tar xzf openssl.tar.gz  && \
    cd openssl-1.1.1i  && \
    ./config  && \
    make  && \
    make install


RUN git clone https://github.com/giltene/wrk2.git  && \
    cd wrk2  && \
    make  && \
    mv wrk /usr/local/bin

WORKDIR /root


CMD /bin/bash
