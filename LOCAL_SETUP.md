# Local Setup Guide (No Docker Required)

This application is designed to run completely locally without Docker. It uses:
- **SQLite** for the database (included with Python, no setup needed)
- **Local Redis** for the job queue (install via package manager)
- **No Docker** required

## Quick Setup

Run the automated setup script:

```bash
./setup_local.sh
```

This will:
1. Create virtual environment
2. Install all Python dependencies
3. Check Redis installation
4. Create `.env` file
5. Initialize SQLite database

## Manual Setup

### 1. Install Redis Locally

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis  # Start on boot
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install redis
sudo systemctl start redis
sudo systemctl enable redis  # Start on boot
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or use your preferred editor
```

Required in `.env`:
```env
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 4. Initialize Database

SQLite database is created automatically, but you can initialize it manually:

```bash
python -c "from app.database import init_db; init_db()"
```

This creates `content_generator.db` in the project directory.

## Running the Application

### Option 1: Use the run script (recommended)

```bash
./run.sh
```

This starts both the RQ worker and FastAPI server.

### Option 2: Manual start (two terminals)

**Terminal 1 - Start RQ Worker:**
```bash
source venv/bin/activate
rq worker --url redis://localhost:6379/0
```

**Terminal 2 - Start FastAPI Server:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 in your browser.

## Database Location

The SQLite database is stored at:
```
./content_generator.db
```

This file is created automatically on first run. You can delete it to reset the database.

## Redis Configuration

Redis runs locally on:
- **Host**: localhost
- **Port**: 6379
- **Database**: 0 (default)

You can change this in `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

## Troubleshooting

### Redis not running
```bash
# Check status
redis-cli ping

# Start Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis
```

### Port 8000 already in use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Database locked errors
- Make sure only one instance of the app is running
- Close any database viewers that might have the DB open
- Delete `content_generator.db` and reinitialize if needed

### Redis connection refused
- Verify Redis is installed: `which redis-server`
- Check if Redis is running: `redis-cli ping`
- Check Redis logs: `tail -f /var/log/redis/redis-server.log` (Linux)

## File Structure

```
.
├── app/
│   ├── database.py          # SQLite database models
│   └── ...
├── content_generator.db     # SQLite database (created automatically)
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── ...
```

## Why No Docker?

This application is designed for local development and doesn't require Docker because:
- SQLite is file-based and works out of the box
- Redis is easy to install via package managers
- No complex orchestration needed for local development
- Faster startup and simpler debugging

For production deployment, you may want to use Docker, but for local development, this setup is simpler and faster.

