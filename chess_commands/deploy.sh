#!/bin/bash

docker build . -t lambda-test:latest
docker tag lambda-test:latest 637454528027.dkr.ecr.us-west-2.amazonaws.com/chess:latest
docker push 637454528027.dkr.ecr.us-west-2.amazonaws.com/chess:latest