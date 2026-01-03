# Production Deployment Guide

This guide explains how to deploy the Multi-Website Content Generator to a production server.

## Quick Deployment

Run the deployment script:

```bash
./deploy.sh
```

The script will:
1. Pull the latest code from the repository
2. Set up Python virtual environment
3. Install all dependencies
4. Build the frontend
5. Initialize the database
6. Start the application in production mode

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Pull Repository

```bash
git pull origin main
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Build Frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

### 4. Configure Environment

Ensure your `.env` file is configured with:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `BACKEND_PORT` - Backend server port (default: 8000)
- `FRONTEND_URL` - Your frontend URL for CORS
- `USE_REDIS` - Set to `true` if using Redis (optional)

### 5. Initialize Database

```bash
source venv/bin/activate
python -c "from app.database import init_db; init_db()"
```

### 6. Start Application

#### Option A: Direct Start (for testing)

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info --access-log --no-reload
```

#### Option B: Using systemd (recommended for production)

1. Copy the service file template:
   ```bash
   cp deploy.service.example /etc/systemd/system/content-generator.service
   ```

2. Edit the service file and update:
   - `User` and `Group` to your application user
   - `WorkingDirectory` to your project path
   - `ExecStart` path to your virtual environment
   - Log file paths

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable content-generator
   sudo systemctl start content-generator
   ```

4. Check status:
   ```bash
   sudo systemctl status content-generator
   ```

#### Option C: Using PM2

```bash
npm install -g pm2
source venv/bin/activate
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4" --name content-generator
pm2 save
pm2 startup
```

#### Option D: Using Supervisor

1. Install supervisor:
   ```bash
   sudo apt-get install supervisor  # Ubuntu/Debian
   ```

2. Create config file `/etc/supervisor/conf.d/content-generator.conf`:
   ```ini
   [program:content-generator]
   command=/path/to/doorway_content_generator/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   directory=/path/to/doorway_content_generator
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/path/to/doorway_content_generator/logs/error.log
   stdout_logfile=/path/to/doorway_content_generator/logs/access.log
   ```

3. Start supervisor:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start content-generator
   ```

## Redis Worker (Optional)

If you're using Redis (`USE_REDIS=true`), you'll also need to run an RQ worker:

```bash
source venv/bin/activate
rq worker --url redis://localhost:6379/0
```

For production, run this as a separate service using systemd, PM2, or Supervisor.

## Environment Variables

Key environment variables in `.env`:

- `OPENROUTER_API_KEY` - Required: Your OpenRouter API key
- `BACKEND_PORT` - Backend server port (default: 8000)
- `FRONTEND_URL` - Frontend URL for CORS (e.g., `https://yourdomain.com`)
- `USE_REDIS` - Set to `true` to use Redis for task queue
- `REDIS_URL` - Redis connection URL (default: `redis://localhost:6379/0`)
- `DATABASE_URL` - Database connection string (default: SQLite)

## Frontend Deployment

The frontend is built and served by the FastAPI backend in production. The built files are in `frontend/dist` and are automatically served at the root path.

If you want to serve the frontend separately (e.g., using Nginx), you can:

1. Build the frontend: `cd frontend && npm run build`
2. Configure Nginx to serve `frontend/dist` as static files
3. Configure the frontend API URL to point to your backend

## Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend static files
    location / {
        root /path/to/doorway_content_generator/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

## SSL/HTTPS

For production, use SSL certificates. You can use Let's Encrypt with Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

- Check application logs: `tail -f logs/backend.log`
- Check systemd logs: `journalctl -u content-generator -f`
- Monitor process: `ps aux | grep uvicorn`

## Troubleshooting

### Application won't start
- Check logs: `tail -f logs/backend.log`
- Verify `.env` file exists and is configured correctly
- Ensure port is not already in use: `lsof -i :8000`
- Check Python virtual environment is activated

### Frontend not loading
- Verify frontend is built: `ls -la frontend/dist`
- Check backend is serving static files (see `app/main.py`)
- Verify CORS settings in `.env`

### Database errors
- Check database file permissions
- Verify `DATABASE_URL` in `.env`
- Try reinitializing: `python -c "from app.database import init_db; init_db()"`

## Security Considerations

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use non-root user** - Run the application as a dedicated user
3. **Enable firewall** - Only expose necessary ports
4. **Use HTTPS** - Always use SSL/TLS in production
5. **Keep dependencies updated** - Regularly update Python and npm packages
6. **Set strong passwords** - For database and admin accounts
7. **Limit CORS origins** - Only allow your frontend domain

## Backup

Regularly backup:
- Database file: `content_generator.db`
- `.env` file (securely)
- Uploaded files (if any)

Example backup script:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
cp content_generator.db "$BACKUP_DIR/content_generator_$DATE.db"
```

