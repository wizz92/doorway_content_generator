# 🚀 Start Here - Local Setup

This application runs **completely locally** with:
- ✅ **SQLite** database (no setup needed, works out of the box)
- ✅ **No Redis required** (uses FastAPI BackgroundTasks by default)
- ❌ **No Docker** required

## Quick Start (3 steps)

### 1. Run Setup Script
```bash
./setup_local.sh
```

### 2. Add Your API Key
Edit `.env` and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_actual_key_here
```

### 3. Create a User
```bash
python create_user.py admin password123
```

### 4. Run the App (Single Command)
```bash
./run.sh
```

This starts both backend and frontend automatically!

Then open http://localhost:5173 in your browser and login.

## What Gets Installed?

- **Python packages** (via pip)
- **SQLite** (already included with Python)
- **Redis** (optional - only if you set `USE_REDIS=true` in `.env`)

## File Locations

- **Database**: `./content_generator.db` (SQLite, created automatically)
- **Config**: `.env` (you create this from `.env.example`)
- **Logs**: `rq_worker.log` (created when worker runs)

## Need Help?

- **Detailed setup**: See [LOCAL_SETUP.md](LOCAL_SETUP.md)
- **Quick reference**: See [QUICKSTART.md](QUICKSTART.md)
- **Full documentation**: See [README.md](README.md)

## Troubleshooting

**Redis not needed!** The app works without Redis by default. See [NO_REDIS_SETUP.md](NO_REDIS_SETUP.md) for details.

**Database issues?**
- SQLite database is created automatically
- Delete `content_generator.db` to reset

**Port 8000 in use?**
- Change port: `uvicorn app.main:app --port 8001`

