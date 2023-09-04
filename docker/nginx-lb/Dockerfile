ARG version=open
FROM nginx-${version}-base:1.0.0

COPY lb-config  /root/lb-config

ENTRYPOINT /docker-entrypoint.sh /bin/sh -c /bin/bash
