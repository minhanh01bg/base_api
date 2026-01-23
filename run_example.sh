#!/bin/bash
# Example script để chạy base application

echo "Starting FastBase AI Application..."
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found!"
    echo "Please create .env file with required environment variables."
    echo ""
fi

# Run application
uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info

