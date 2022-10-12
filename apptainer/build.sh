#! /bin/bash

# usage: ./build.sh [prp|poprp] <docker image name> <output sif>
if [[ "$#" -lt 3 ]]; then
    echo "usage: ./build.sh [prp|poprp] <docker image name> <output sif>"
    exit 1
fi

# check if building prp or poprp
if [ "$1" = "prp" ]; then
    echo "Building PRP"
    cp Dockerfile.prp Dockerfile
elif [ "$1" = "poprp" ]; then
    echo "Building POPRP"
    cp Dockerfile.poprp Dockerfile
else
    echo "Please specify prp or poprp"
    exit 1
fi

# build the docker image
docker build -t $2 .

# export the docker image to a sif file
apptainer build $3 docker-daemon://$2:latest

# remove the docker image
docker rmi $2

# remove the Dockerfile
rm Dockerfile
