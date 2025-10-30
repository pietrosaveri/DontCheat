#!/bin/bash

cd "$(dirname "$0")"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Loaded environment variables from .env"
else
    echo "⚠ Warning: .env file not found"
    echo "Please create a .env file with your API keys"
    exit 1
fi

# Check if already running
if [ -f .cheatme.pid ] && kill -0 $(cat .cheatme.pid) 2>/dev/null; then
    echo "CheatMe is already running (PID: $(cat .cheatme.pid))"
    exit 1
fi

# Start in background with logging
nohup .venv/bin/python main.py > cheatme.log 2>&1 &
PID=$!
echo $PID > .cheatme.pid

echo ""
echo "CheatMe started in background"
echo "PID: $PID"
echo "AI Provider: ${AI_PROVIDER:-groq}"
echo ""
echo "Gestures:"
echo "  • 3-tap: Instant analysis"
echo "  • Option + 3-tap: Save reference context"
echo "  • Control + 3-tap: Analyze with saved context"
echo ""
echo "Logs: tail -f cheatme.log"
echo "To stop: ./stop.sh"