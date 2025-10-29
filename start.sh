#!/bin/bash

cd "$(dirname "$0")"

# Check if already running
if [ -f .cheatme.pid ] && kill -0 $(cat .cheatme.pid) 2>/dev/null; then
    echo "CheatMe is already running (PID: $(cat .cheatme.pid))"
    exit 1
fi

# Start in background
nohup .venv/bin/python main.py > /dev/null 2>&1 &
PID=$!
echo $PID > .cheatme.pid

echo "CheatMe started silently in background"
echo "PID: $PID"
echo "To stop: ./stop.sh"