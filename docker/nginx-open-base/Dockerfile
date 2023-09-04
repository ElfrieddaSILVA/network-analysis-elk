FROM nginx:1.22.0

RUN apt-get update  && \
    apt-get install -y --no-install-recommends \
        net-tools \
        iproute2 \
        iputils-ping \
    && \
    rm -rf /var/lib/apt/lists/*


ENTRYPOINT /docker-entrypoint.sh /bin/sh -c /bin/bash
