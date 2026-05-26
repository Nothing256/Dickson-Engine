#!/bin/bash
make dickson_bench -C build
./build/bin/dickson_bench 13 2 14 --random &
PID=$!
sleep 1
kill -ABRT $PID
