#!/bin/bash
MAX_NUM=100
for i in $(seq 1 $MAX_NUM); do
    echo $ip
    ip="$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255)).$((1 + $RANDOM % 255))"
    curl --unix-socket /tmp/sanic.sock "http://localhost/?ip=$ip&ex=3%20minutes"
done
# sudo ufw reset
