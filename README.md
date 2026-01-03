# Multi-Website Content Generator

A web application that generates unique content variations for multiple websites from a CSV file of keywords. Each website receives different content for the same keywords based on language, geography, and website-specific variations.

## Features

- 📁 **CSV Upload**: Upload CSV files with keywords (must contain a "keyword" column)
- 🌍 **Multi-Language & Geography**: Configure language (lang) and geography (geo) parameters
- 🔢 **Multiple Websites**: Generate content for 1-100 websites
- 🎨 **Content Variations**: Each website gets unique content variations for the same keywords
- 📊 **Progress Tracking**: Real-time progress updates during content generation
- 📦 **ZIP Download**: Download all generated files as a ZIP archive
- ⚡ **Background Processing**: Asynchronous job queue for long-running tasks

## Requirements

- Python 3.8+
- OpenRouter API key
- SQLite (included with Python, no setup needed)
- Redis (optional - only needed if you set `USE_REDIS=true` in `.env`)

## Installation (Local Setup - No Docker)

### Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup_local.sh
```

This will set up everything automatically. See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed instructions.

### Manual Setup

1. **Install Redis locally** (no Docker needed):
```bash
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
redis-cli ping  # Should return: PONG
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

5. **Initialize SQLite database** (automatic, but you can do it manually):
```bash
python -c "from app.database import init_db; init_db()"
```

The SQLite database (`content_generator.db`) will be created automatically in the project directory.

## Running the Application

### Quick Start (Single Command)

Simply run:
```bash
./run.sh
```

This will:
- ✅ Start the backend server (port 8000)
- ✅ Start the frontend server (port 5173)
- ✅ Initialize database if needed
- ✅ Install dependencies if needed

Then:
1. Create a user account (in a new terminal):
```bash
python create_user.py username password
```

2. Open http://localhost:5173 in your browser

3. Login with the credentials you created

### Manual Start (Separate Terminals)

If you prefer to run services separately:

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

### Production Build

Build the frontend:
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/` and can be served by FastAPI or any web server.

### With Redis (Optional)

If you want to use Redis for better job queue management:

1. Set `USE_REDIS=true` in `.env`
2. Start Redis: `brew services start redis` (macOS) or `sudo systemctl start redis` (Linux)
3. Start the RQ worker (in a separate terminal):
```bash
source venv/bin/activate
rq worker --url redis://localhost:6379/0
```
4. Start the FastAPI server:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. **Upload CSV File**: 
   - Click or drag-and-drop a CSV file containing a "keyword" column
   - The file will be validated and keywords will be extracted

2. **Configure Parameters**:
   - **Language Code**: e.g., "hu" (Hungarian), "en" (English), "de" (German)
   - **Geography Code**: e.g., "HU" (Hungary), "US" (United States), "DE" (Germany)
   - **Number of Websites**: Enter a number between 1 and 100

3. **Generate Content**:
   - Click "Generate Content" to start the process
   - Monitor progress in real-time
   - Wait for completion

4. **Download Results**:
   - Once completed, click "Download Results"
   - A ZIP file will be downloaded containing one file per website
   - Each file follows the format: `website-{index}-{lang}-{geo}.txt`
   - File format: `keyword ;; <h1>...</h1><p>...</p>` (one entry per line)

## API Endpoints

### POST `/api/upload`
Upload a CSV file with keywords.

**Request**: multipart/form-data with CSV file
**Response**: 
```json
{
  "job_id": "uuid",
  "keywords_count": 10,
  "preview": ["keyword1", "keyword2", ...]
}
```

### POST `/api/generate`
Start content generation for a job.

**Request**:
```json
{
  "job_id": "uuid",
  "lang": "hu",
  "geo": "HU",
  "num_websites": 3
}
```

**Response**:
```json
{
  "status": "queued",
  "estimated_time": 300,
  "job_id": "uuid"
}
```

### GET `/api/job/{job_id}/status`
Get the status of a job.

**Response**:
```json
{
  "id": "uuid",
  "status": "processing",
  "progress": 45,
  "keywords_completed": 5,
  "total_keywords": 10,
  "websites_completed": 1,
  "num_websites": 3
}
```

### GET `/api/job/{job_id}/download`
Download generated content files as ZIP archive.

**Response**: ZIP file with content files

### GET `/api/jobs`
List recent jobs.

**Response**: Array of job objects

## Configuration

Environment variables (in `.env` file):

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `MAX_KEYWORDS`: Maximum keywords per job (default: 1000)
- `MAX_WEBSITES`: Maximum websites per job (default: 100)
- `REQUEST_DELAY_SECONDS`: Delay between API calls (default: 2.0)
- `TASK_TIMEOUT`: Timeout for content generation in seconds (default: 300)
- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379/0)
- `DATABASE_URL`: Database connection URL (default: sqlite:///./content_generator.db)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database models and setup
│   ├── tasks.py              # Background tasks
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py         # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── file_processor.py    # CSV processing
│       ├── openrouter_client.py  # OpenRouter API client
│       ├── content_generator.py  # Content generation service
│       └── output_formatter.py   # Output formatting
├── requirements.txt
├── .env.example
└── README.md
```

## Content Format

Generated content follows the `combined_articles.txt` format:

```
keyword1 ;; <h1>Title</h1><p>Content...</p>
keyword2 ;; <h1>Title</h1><p>Content...</p>
```

Each line contains:
- Keyword
- Two semicolons (`;;`) as separator
- HTML content (no line breaks within content)

## Notes

- Content is generated using OpenRouter API
- Each website gets unique content variations for the same keywords
- Content length: 450-550 words
- Only HTML tags allowed: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`
- Rate limiting is applied to respect API limits

## Troubleshooting

1. **Redis connection error**: 
   - Make sure Redis is installed and running locally
   - Test with: `redis-cli ping` (should return PONG)
   - Start Redis: `brew services start redis` (macOS) or `sudo systemctl start redis` (Linux)

2. **OpenRouter API errors**: 
   - Check your API key in `.env` file
   - Verify you have credits/balance in your OpenRouter account

3. **Job stuck in "queued"**: 
   - Make sure the RQ worker is running in a separate terminal
   - Check `rq_worker.log` for errors
   - Restart the worker if needed

4. **Database errors**: 
   - SQLite database is created automatically
   - If needed, reinitialize: `python -c "from app.database import init_db; init_db()"`

5. **Port already in use**: 
   - Change the port in the uvicorn command or kill the process using port 8000

## License

MIT

