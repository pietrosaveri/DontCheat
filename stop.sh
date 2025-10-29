#!/bin/bash

cd "$(dirname "$0")"

if [ ! -f .cheatme.pid ]; then
    echo "CheatMe is not running"
    exit 1
fi

PID=$(cat .cheatme.pid)

if kill -0 $PID 2>/dev/null; then
    kill $PID
    rm .cheatme.pid
    echo "CheatMe stopped (PID: $PID)"
else
    rm .cheatme.pid
    echo "CheatMe was not running (cleaned up stale PID file)"
fi