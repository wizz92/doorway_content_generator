#!/bin/bash

# Local setup script for Multi-Website Content Generator
# This script sets up everything needed to run locally (no Docker)

set -e

echo "🚀 Setting up Multi-Website Content Generator (Local Version)"
echo "=============================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
    else
        echo "⚠️  .env.example not found, creating basic .env file..."
        cat > .env << EOF
OPENROUTER_API_KEY=your_openrouter_api_key_here
MAX_KEYWORDS=1000
MAX_WEBSITES=100
REQUEST_DELAY_SECONDS=2.0
TASK_TIMEOUT=300
USE_REDIS=false
DATABASE_URL=sqlite:///./content_generator.db
EOF
        echo "✅ Created .env file"
        echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
    fi
else
    echo "✅ .env file already exists"
fi
echo ""

# Initialize database
echo "💾 Initializing SQLite database..."
python -c "from app.database import init_db; init_db()" 2>/dev/null || {
    echo "⚠️  Database initialization had warnings (this is usually fine)"
}
echo "✅ Database initialized"
echo ""

echo "=============================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENROUTER_API_KEY"
echo "  2. Run the application: ./run.sh"
echo ""
echo "Or start manually:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "ℹ️  Note: The app runs without Redis by default using FastAPI BackgroundTasks"
echo "   No additional services needed for local development!"
echo ""

