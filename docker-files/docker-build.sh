#!/bin/sh
if [ ! -f Dockerfile ]; then
   echo "No Dockerfile found in this directory.";
   exit 1;
fi

IMAGENAME="durak"
IMAGETAG="latest"

# build Docker image
docker build --pull --no-cache --force-rm -t ${IMAGENAME}:${IMAGETAG} .