#/usr/bin/env bash

set -e

nginx_version=


usage_info() {
    printf "Usage: ./build.sh <base>\n"
    printf "  Base options:\n"
    printf "    open\t open-source nginx\n"
    printf "    plus\t nginx plus \t[you need to provide your\n"
    printf "\t\t\t\t subscription keys to the\n"
    printf "\t\t\t\t directory nginx-plus-base]\n\n"
    printf "  Using can need root priviledges for docker command\n\n"
}



if [[ $# > 0 ]] ; then
    if [[ $1 == "open" ]] ; then
        echo "Building on Open Source nginx"
        nginx_version="open"
        nginx_flags=""
    elif [[ $1 == "plus" ]] ; then
        echo "Building on nginx plus"
        nginx_version="plus"
        nginx_flags="--secret id=nginx-crt,src=./nginx-plus-base/nginx-repo.crt --secret id=nginx-key,src=./nginx-plus-base/nginx-repo.key"
    else
        usage_info
        exit 1
    fi
else
    usage_info
    exit 1
fi


# base images
echo "Building nginx image ${nginx_version}..."
DOCKER_BUILDKIT=1 docker build -f ./nginx-${nginx_version}-base/Dockerfile ${nginx_flags} -t nginx-${nginx_version}-base:1.0.0 nginx-${nginx_version}-base



echo "Building nginx load balancer image..."
docker build -f ./nginx-lb/Dockerfile --build-arg version=${nginx_version} -t nginx-${nginx_version}-lb nginx-lb

echo "Building simple flask server image..."
docker build -f ./simple-srv/Dockerfile -t flask simple-srv

echo "Building nginx based matrix server image..."
docker build -f ./nginx-srv/Dockerfile --build-arg version=${nginx_version} -t nginx-${nginx_version}-srv nginx-srv

echo "Building wrk2 image..."
docker build -f ./wrk2/Dockerfile -t wrk2 wrk2

echo "Building sysbench image..."
docker build -t sysbench:latest -f ./sysbench/Dockerfile.benchmark .

echo "Building sysbench image..."
docker build -t tip-postgres:latest -f ./postgresql-db/Dockerfile.postgres .

echo "Building elasticsearch image..."
docker build -t elasticsearch:latest -f ./elasticsearch/Dockerfile .

echo "Building kibana image..."
docker build -t kibana:latest -f ./kibana/Dockerfile .