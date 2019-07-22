#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`
source $CD/local_env.sh

nodemon --exec python3 ./main.py
