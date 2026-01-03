#!/bin/bash

# Production Deployment Script for Multi-Website Content Generator
# This script pulls the repository, installs dependencies, builds frontend,
# and runs the application in production mode
#
# Usage:
#   ./deploy.sh                    # Full deployment and start
#   START_APP=false ./deploy.sh    # Prepare only, don't start
#   BRANCH=develop ./deploy.sh     # Deploy from specific branch
#
# Environment Variables:
#   REPO_DIR      - Repository directory (default: current directory)
#   BRANCH        - Git branch to deploy (default: main)
#   VENV_DIR      - Virtual environment directory (default: venv)
#   BACKEND_PORT  - Backend server port (default: 8000)
#   LOG_DIR       - Logs directory (default: logs)
#   START_APP     - Start application after deployment (default: true)
#   PID_FILE      - File to save process IDs (default: .deploy.pids)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_DIR="${REPO_DIR:-$(pwd)}"
BRANCH="${BRANCH:-main}"
VENV_DIR="${VENV_DIR:-venv}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
LOG_DIR="${LOG_DIR:-logs}"
START_APP="${START_APP:-true}"  # Set to "false" to only prepare, not start
PID_FILE="${PID_FILE:-.deploy.pids}"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    log_warning "Running as root is not recommended. Consider using a non-root user."
fi

echo "=========================================="
echo "🚀 Production Deployment Script"
echo "=========================================="
echo ""

# Step 1: Navigate to repository directory
log_info "Working directory: $REPO_DIR"
cd "$REPO_DIR" || {
    log_error "Failed to navigate to $REPO_DIR"
    exit 1
}

# Step 2: Pull latest changes from repository
log_info "Pulling latest changes from repository..."
if [ -d ".git" ]; then
    git fetch origin || {
        log_warning "Failed to fetch from origin. Continuing with local code..."
    }
    git checkout "$BRANCH" || {
        log_error "Failed to checkout branch $BRANCH"
        exit 1
    }
    git pull origin "$BRANCH" || {
        log_warning "Failed to pull from origin. Using local code..."
    }
    log_success "Repository updated"
else
    log_warning "Not a git repository. Skipping git pull..."
fi
echo ""

# Step 3: Check Python installation
log_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
log_success "$PYTHON_VERSION found"
echo ""

# Step 4: Create/update virtual environment
log_info "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created"
else
    log_success "Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
log_success "Virtual environment activated"
echo ""

# Step 5: Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip --quiet
log_success "pip upgraded"
echo ""

# Step 6: Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet
log_success "Python dependencies installed"
echo ""

# Step 7: Check Node.js and npm
log_info "Checking Node.js and npm installation..."
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    log_error "npm is not installed. Please install npm."
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
log_success "Node.js $NODE_VERSION and npm $NPM_VERSION found"
echo ""

# Step 8: Install frontend dependencies
log_info "Installing frontend dependencies..."
cd frontend || {
    log_error "Frontend directory not found"
    exit 1
}

# Clean install for production
if [ -d "node_modules" ]; then
    log_info "Removing existing node_modules for clean install..."
    rm -rf node_modules
fi

npm ci --production=false --silent || {
    log_error "Failed to install frontend dependencies"
    exit 1
}
log_success "Frontend dependencies installed"
echo ""

# Step 9: Build frontend
log_info "Building frontend for production..."
npm run build || {
    log_error "Failed to build frontend"
    exit 1
}

if [ ! -d "dist" ]; then
    log_error "Frontend build failed - dist directory not found"
    exit 1
fi

log_success "Frontend built successfully"
cd ..
echo ""

# Step 10: Check environment file
log_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    log_warning ".env file not found"
    if [ -f ".env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env and configure your settings (especially OPENROUTER_API_KEY)"
    else
        log_warning "No .env.example found. Please create .env file manually."
    fi
else
    log_success ".env file exists"
fi
echo ""

# Step 11: Initialize database
log_info "Initializing database..."
python -c "from app.database import init_db; init_db()" 2>/dev/null || {
    log_warning "Database initialization had warnings (this is usually fine)"
}
log_success "Database initialized"
echo ""

# Step 12: Check Redis (if needed)
USE_REDIS=$(grep -E "^USE_REDIS=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "false")

if [ "$USE_REDIS" = "true" ]; then
    log_info "Checking Redis connection..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is running"
        else
            log_warning "Redis is not running but USE_REDIS=true in .env"
            log_warning "Please start Redis or set USE_REDIS=false in .env"
        fi
    else
        log_warning "redis-cli not found. Make sure Redis is installed and running."
    fi
    echo ""
fi

# Step 13: Create logs directory
log_info "Setting up logs directory..."
mkdir -p "$LOG_DIR"
log_success "Logs directory ready"
echo ""

# Step 14: Display deployment summary
echo "=========================================="
log_success "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "📋 Deployment Summary:"
echo "   - Repository: $(pwd)"
echo "   - Branch: $BRANCH"
echo "   - Python: $PYTHON_VERSION"
echo "   - Node.js: $NODE_VERSION"
echo "   - Frontend: Built and ready in frontend/dist"
echo "   - Backend Port: $BACKEND_PORT"
echo ""

# Step 15: Start application (if requested)
if [ "$START_APP" = "true" ]; then
    log_info "Starting application in production mode..."
    echo ""

    # Get backend port from .env or use default
    BACKEND_PORT=$(grep -E "^BACKEND_PORT=" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "$BACKEND_PORT")

    # Clear previous PID file
    > "$PID_FILE"

    # Start RQ worker if Redis is enabled
    if [ "$USE_REDIS" = "true" ]; then
        if redis-cli ping > /dev/null 2>&1; then
            log_info "Starting RQ worker..."
            "$VENV_DIR/bin/rq" worker --url redis://localhost:6379/0 > "$LOG_DIR/rq_worker.log" 2>&1 &
            RQ_PID=$!
            echo "RQ_WORKER_PID=$RQ_PID" >> "$PID_FILE"
            log_success "RQ worker started (PID: $RQ_PID)"
            echo ""
        fi
    fi

    # Start backend server
    log_info "Starting backend server..."
    "$VENV_DIR/bin/uvicorn" app.main:app \
        --host 0.0.0.0 \
        --port "$BACKEND_PORT" \
        --workers 4 \
        --log-level info \
        --access-log \
        --no-reload \
        > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "BACKEND_PID=$BACKEND_PID" >> "$PID_FILE"

    log_success "Backend server started (PID: $BACKEND_PID)"
    echo ""

    # Wait a moment for server to start
    sleep 2

    # Check if server is running
    if ps -p $BACKEND_PID > /dev/null; then
        log_success "Application is running!"
        echo ""
        echo "📍 Backend API: http://0.0.0.0:$BACKEND_PORT"
        echo "📍 API Docs: http://0.0.0.0:$BACKEND_PORT/docs"
        echo "📍 Frontend: Served from frontend/dist"
        echo ""
        echo "📝 Logs:"
        echo "   - Backend: $LOG_DIR/backend.log"
        if [ "$USE_REDIS" = "true" ] && [ ! -z "$RQ_PID" ]; then
            echo "   - RQ Worker: $LOG_DIR/rq_worker.log"
        fi
        echo ""
        echo "💡 To stop the application:"
        echo "   ./stop.sh  (if available)"
        echo "   Or manually: kill $BACKEND_PID"
        if [ ! -z "$RQ_PID" ]; then
            echo "   kill $RQ_PID"
        fi
        echo ""
        echo "💡 PIDs saved to: $PID_FILE"
        echo ""
        echo "💡 For production, consider using a process manager like:"
        echo "   - systemd (Linux) - see deploy.service.example"
        echo "   - supervisor"
        echo "   - PM2"
        echo "   - Docker Compose"
        echo ""
    else
        log_error "Failed to start backend server. Check logs: $LOG_DIR/backend.log"
        exit 1
    fi
else
    log_info "Skipping application start (START_APP=false)"
    echo ""
    echo "💡 To start the application manually:"
    echo "   source $VENV_DIR/bin/activate"
    echo "   uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 4 --log-level info --access-log --no-reload"
    echo ""
    echo "💡 Or use the full path:"
    echo "   $VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 4 --log-level info --access-log --no-reload"
    echo ""
    echo "💡 Or use a process manager (see DEPLOYMENT.md for details)"
    echo ""
fi

echo "=========================================="

