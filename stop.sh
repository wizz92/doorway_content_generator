#!/bin/bash

# Stop script for Multi-Website Content Generator
# Stops processes started by deploy.sh

PID_FILE="${PID_FILE:-.deploy.pids}"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ PID file not found: $PID_FILE"
    echo "   Application may not be running or was started differently"
    exit 1
fi

echo "🛑 Stopping Multi-Website Content Generator..."
echo ""

# Read PIDs from file
if [ -f "$PID_FILE" ]; then
    source "$PID_FILE"
    
    if [ ! -z "$BACKEND_PID" ]; then
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            echo "✅ Backend server stopped (PID: $BACKEND_PID)"
        else
            echo "⚠️  Backend process (PID: $BACKEND_PID) not found"
        fi
    fi
    
    if [ ! -z "$RQ_WORKER_PID" ]; then
        if ps -p $RQ_WORKER_PID > /dev/null 2>&1; then
            kill $RQ_WORKER_PID
            echo "✅ RQ worker stopped (PID: $RQ_WORKER_PID)"
        else
            echo "⚠️  RQ worker process (PID: $RQ_WORKER_PID) not found"
        fi
    fi
    
    # Remove PID file
    rm -f "$PID_FILE"
    echo ""
    echo "✅ All processes stopped"
else
    echo "❌ PID file not found"
    exit 1
fi

