#!/bin/bash

# Start script for the Multi-Website Content Generator
# Starts both backend and frontend with a single command

echo "🚀 Starting Multi-Website Content Generator..."
echo "=============================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "  ✓ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "  ✓ Frontend stopped"
    fi
    if [ ! -z "$RQ_PID" ]; then
        kill $RQ_PID 2>/dev/null
        echo "  ✓ RQ worker stopped"
    fi
    exit
}

trap cleanup EXIT INT TERM

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing backend dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/.installed
    echo "  ✓ Backend dependencies installed"
fi

# Check if Redis is needed and available
USE_REDIS=$(grep -E "^USE_REDIS=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "false")

if [ "$USE_REDIS" = "true" ]; then
    echo "🔍 Checking Redis..."
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "❌ Redis is not running but USE_REDIS=true in .env"
        echo "   Please start Redis or set USE_REDIS=false in .env"
        exit 1
    else
        echo "  ✓ Redis is running"
        # Start RQ worker in background
        echo "  🔄 Starting RQ worker..."
        rq worker --url redis://localhost:6379/0 > rq_worker.log 2>&1 &
        RQ_PID=$!
        echo "  ✓ RQ worker started (PID: $RQ_PID)"
    fi
else
    echo "ℹ️  Running without Redis (using FastAPI BackgroundTasks)"
fi

# Initialize database
echo "💾 Initializing database..."
python -c "from app.database import init_db; init_db()" 2>/dev/null || echo "  ✓ Database already initialized"

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install > /dev/null 2>&1
    cd ..
    echo "  ✓ Frontend dependencies installed"
fi

# Get backend port from .env or use default (keep in sync with .env / Vite proxy)
BACKEND_PORT=$(grep -E "^BACKEND_PORT=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "8002")

# Get frontend port from .env or fallback (matches Vite config: VITE_PORT/PORT -> 3021)
FRONTEND_PORT=$(grep -E "^VITE_PORT=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"')
if [ -z "$FRONTEND_PORT" ]; then
    FRONTEND_PORT=$(grep -E "^PORT=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"')
fi
if [ -z "$FRONTEND_PORT" ]; then
    FRONTEND_PORT=3021
fi

# Prefer FRONTEND_URL (from .env) for display; fall back to localhost:port
FRONTEND_URL=$(grep -E "^FRONTEND_URL=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"')
if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="http://localhost:$FRONTEND_PORT"
fi

# Start backend in background
echo ""
echo "🔧 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!
echo "  ✓ Backend started (PID: $BACKEND_PID) on http://localhost:$BACKEND_PORT"

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "  ✓ Frontend started (PID: $FRONTEND_PID) on $FRONTEND_URL"

echo ""
echo "=============================================="
echo "✅ Application is running!"
echo ""
echo "📍 Frontend: $FRONTEND_URL"
echo "📍 Backend API: http://localhost:$BACKEND_PORT"
echo "📍 API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "📝 Logs:"
echo "   - Backend: backend.log"
echo "   - Frontend: frontend.log"
if [ "$USE_REDIS" = "true" ]; then
    echo "   - RQ Worker: rq_worker.log"
fi
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================="
echo ""

# Wait for user interrupt
wait

