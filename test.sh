#!/bin/bash
# test max rules num
MAX_NUM=30000
for i in $(seq 1 $MAX_NUM); do
    echo $ip
    ip="$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255))"
    curl --unix-socket /tmp/sanic.sock "http://localhost/?ip=$ip"
done
# sudo ufw reset
