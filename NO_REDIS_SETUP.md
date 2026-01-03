# Running Without Redis

The application now works **completely without Redis**! By default, it uses FastAPI's built-in `BackgroundTasks` for asynchronous job processing.

## Default Behavior (No Redis)

The app is configured to run without Redis by default:
- ✅ Uses FastAPI `BackgroundTasks` for background job processing
- ✅ Stores all job state in SQLite database
- ✅ No external dependencies required
- ✅ Simpler setup and deployment

## Configuration

In your `.env` file:
```env
USE_REDIS=false  # Set to false (default) to run without Redis
```

## Running the App

Simply run:
```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**No Redis worker needed!** The background tasks run automatically.

## How It Works

1. **Job Creation**: When you upload a CSV and start generation, a job is created in SQLite
2. **Background Processing**: FastAPI's `BackgroundTasks` runs the content generation asynchronously
3. **Progress Updates**: Job progress is stored in SQLite and can be polled via the status endpoint
4. **Completion**: When done, the job status is updated and files are ready for download

## Optional: Using Redis

If you want to use Redis for better job queue management (useful for production or multiple workers):

1. Install Redis:
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Linux
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

2. Install Redis dependencies:
   ```bash
   pip install redis rq
   ```

3. Set in `.env`:
   ```env
   USE_REDIS=true
   ```

4. Start RQ worker (in separate terminal):
   ```bash
   rq worker --url redis://localhost:6379/0
   ```

5. Start the app as usual

## Benefits of No-Redis Mode

- ✅ **Simpler setup**: No need to install/configure Redis
- ✅ **Fewer dependencies**: One less service to manage
- ✅ **Easier local development**: Just run the FastAPI server
- ✅ **Works out of the box**: Perfect for local testing

## Limitations

- Background tasks run in the same process (not distributed)
- If the server restarts, running jobs will be lost (they'll need to be restarted)
- For production with high load, Redis is recommended

For local development and testing, the no-Redis mode is perfect!

