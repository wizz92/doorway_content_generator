# Local Setup Guide (No Docker Required)

This application is designed to run completely locally without Docker. It uses:
- **SQLite** for the database (included with Python, no setup needed)
- **FastAPI BackgroundTasks** for job processing (no Redis needed!)
- **No Docker** required
- **No Redis** required for local development

## Quick Setup

Run the automated setup script:

```bash
./setup_local.sh
```

This will:
1. Create virtual environment
2. Install all Python dependencies
3. Create `.env` file
4. Initialize SQLite database

## Manual Setup

### 1. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or use your preferred editor
```

Required in `.env`:
```env
OPENROUTER_API_KEY=your_actual_api_key_here
USE_REDIS=false  # Set to false to use FastAPI BackgroundTasks (default)
```

### 3. Initialize Database

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

This starts the FastAPI server. No Redis worker needed!

### Option 2: Manual start

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 in your browser.

**Note:** The app uses FastAPI's built-in `BackgroundTasks` for job processing, so no separate worker process is needed!

## Database Location

The SQLite database is stored at:
```
./content_generator.db
```

This file is created automatically on first run. You can delete it to reset the database.

## How It Works (No Redis Mode)

The application uses FastAPI's `BackgroundTasks` for asynchronous job processing:
- ✅ Jobs run in the background automatically
- ✅ No Redis or external services needed
- ✅ All job state stored in SQLite database
- ✅ Perfect for local development

To use Redis (optional, for production):
1. Set `USE_REDIS=true` in `.env`
2. Install and start Redis
3. Start an RQ worker in a separate terminal

See `NO_REDIS_SETUP.md` for more details.

## Troubleshooting

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

## Why No Docker or Redis?

This application is designed for local development and doesn't require Docker or Redis because:
- SQLite is file-based and works out of the box
- FastAPI BackgroundTasks handles job processing without external services
- No complex orchestration needed for local development
- Faster startup and simpler debugging
- One less service to manage and configure

For production deployment, you may want to use Docker and Redis, but for local development, this setup is simpler and faster.

