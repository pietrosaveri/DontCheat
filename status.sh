#!/bin/bash

cd "$(dirname "$0")"

if [ ! -f .cheatme.pid ]; then
    echo "CheatMe is not running"
    exit 1
fi

PID=$(cat .cheatme.pid)

if kill -0 $PID 2>/dev/null; then
    echo "CheatMe is running"
    echo "PID: $PID"
    echo "Started: $(ps -p $PID -o lstart=)"
else
    rm .cheatme.pid
    echo "CheatMe is not running (cleaned up stale PID file)"
fi