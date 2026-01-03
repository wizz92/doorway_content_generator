# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed (SQLite included, no setup needed)
2. **Redis** installed locally (no Docker required)
3. **OpenRouter API Key** (get one at https://openrouter.ai)

## Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd /Users/wizz/coding/content_for_doorway_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 5. Install and start Redis locally:
# macOS (Homebrew):
brew install redis
brew services start redis

# Linux (Ubuntu/Debian):
sudo apt-get install redis-server
sudo systemctl start redis

# Linux (Fedora/RHEL):
sudo dnf install redis
sudo systemctl start redis

# Verify Redis is running:
redis-cli ping
# Should return: PONG

# 6. Initialize database
python -c "from app.database import init_db; init_db()"
```

## Running the Application

### Option 1: Single Command (Easiest)

```bash
./run.sh
```

This automatically starts:
- ✅ Backend server (port 8000)
- ✅ Frontend server (port 5173)
- ✅ RQ worker (if Redis is enabled)

Then:
1. Create a user account (in a new terminal):
```bash
python create_user.py admin password123
```

2. Open http://localhost:5173 in your browser

3. Login with the credentials you created

### Option 2: Manual Start (Separate Terminals)

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Using the Application

1. **Login** at http://localhost:5173 with your credentials

2. **Prepare your CSV file** with a "keyword" column:
   ```csv
   keyword
   keyword 1
   keyword 2
   keyword 3
   ```

3. **Upload the CSV** via the web interface

4. **Configure parameters**:
   - Language: e.g., "hu" (Hungarian), "en" (English)
   - Geography: e.g., "HU" (Hungary), "US" (United States)
   - Number of Websites: 1-100

5. **Click "Create Job"** and monitor progress in real-time

6. **Download the ZIP file** when the job completes

## Testing

Run the test suite:

```bash
source venv/bin/activate
pytest
```

## Troubleshooting

### Redis connection error
```bash
# Check if Redis is installed and running
redis-cli ping
# Should return: PONG

# If not installed:
# macOS:
brew install redis
brew services start redis

# Linux (Ubuntu/Debian):
sudo apt-get install redis-server
sudo systemctl start redis

# Linux (Fedora/RHEL):
sudo dnf install redis
sudo systemctl start redis
```

### OpenRouter API errors
- Verify your API key in `.env` file
- Check your OpenRouter account balance
- Ensure you have API access enabled

### Job stuck in "queued" status
- Make sure the RQ worker is running
- Check `rq_worker.log` for errors
- Restart the worker if needed

### Database errors
```bash
# Reinitialize database
python -c "from app.database import init_db; init_db()"
```

## Example CSV File

Create a file `keywords.csv`:

```csv
keyword
30bet Casino 50 Free Spins
5 6 Lottószámok
7 Lotto Nyerőszámok
Alf Casino Hu 2025 Review
Fairspin Casino Befizetés Nélküli Bónusz
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check API endpoints at http://localhost:8000/docs (Swagger UI)
- Customize prompts in `app/services/openrouter_client.py`

