#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${DIR}
echo ${DIR}
git fetch
git checkout HEAD ${DIR}/src/
cd src
kill -9 $("cat hausnortuf_pid.txt")
sudo python3.6 Main.py
