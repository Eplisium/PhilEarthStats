# Deployment Guide

This guide covers various deployment options for PhilEarthStats.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Manual Production Deployment](#manual-production-deployment)
4. [Cloud Platforms](#cloud-platforms)

---

## Local Development

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed local development instructions.

**Quick Start:**
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed (optional)

### Build and Run with Docker

**Option 1: Using Docker Compose (Recommended)**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Option 2: Using Docker directly**

```bash
# Build the image
docker build -t philearthstats .

# Run the container
docker run -d -p 5000:5000 --name philearthstats philearthstats

# View logs
docker logs -f philearthstats

# Stop and remove
docker stop philearthstats
docker rm philearthstats
```

**Access the application:**
- Open browser to `http://localhost:5000`

---

## Manual Production Deployment

### Backend (Flask)

#### 1. Prepare Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install gunicorn  # Production server
```

#### 2. Run with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Production Configuration:**
```bash
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  app:app
```

#### 3. Create Systemd Service (Linux)

Create `/etc/systemd/system/philearthstats.service`:

```ini
[Unit]
Description=PhilEarthStats Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/philearthstats/backend
Environment="PATH=/opt/philearthstats/backend/venv/bin"
ExecStart=/opt/philearthstats/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start philearthstats
sudo systemctl enable philearthstats
sudo systemctl status philearthstats
```

### Frontend (React)

#### 1. Build for Production

```bash
cd frontend
npm install
npm run build
```

This creates an optimized build in `frontend/dist/`

#### 2. Serve Static Files

**Option A: Nginx**

Create `/etc/nginx/sites-available/philearthstats`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    root /opt/philearthstats/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/philearthstats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option B: Apache**

Create `/etc/apache2/sites-available/philearthstats.conf`:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /opt/philearthstats/frontend/dist

    <Directory /opt/philearthstats/frontend/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        FallbackResource /index.html
    </Directory>

    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:5000/api/
    ProxyPassReverse /api/ http://127.0.0.1:5000/api/

    ErrorLog ${APACHE_LOG_DIR}/philearthstats-error.log
    CustomLog ${APACHE_LOG_DIR}/philearthstats-access.log combined
</VirtualHost>
```

Enable and restart Apache:
```bash
sudo a2ensite philearthstats
sudo a2enmod proxy proxy_http
sudo systemctl restart apache2
```

---

## Cloud Platforms

### Heroku

1. **Create `Procfile` in root:**
```
web: cd backend && gunicorn app:app
```

2. **Create `runtime.txt`:**
```
python-3.11.0
```

3. **Deploy:**
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04 recommended)
2. **SSH into instance**
3. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```
4. **Clone repository**
5. **Follow Manual Production Deployment steps above**

### Google Cloud Platform

1. **Create `app.yaml`:**
```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT app:app

instance_class: F2

handlers:
  - url: /static
    static_dir: static
  - url: /.*
    script: auto
```

2. **Deploy:**
```bash
gcloud app deploy
```

### DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure build settings:**
   - Build Command: `cd frontend && npm install && npm run build`
   - Run Command: `cd backend && gunicorn app:app`
3. **Deploy**

### Vercel (Frontend) + Backend Separate

**Frontend on Vercel:**
```bash
cd frontend
vercel deploy
```

**Backend on Railway/Render/Fly.io:**
- Connect repository
- Set root directory to `backend/`
- Deploy

---

## SSL/HTTPS Configuration

### Using Let's Encrypt (Certbot)

```bash
sudo apt install certbot python3-certbot-nginx

# For Nginx
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Environment Variables

Create `.env` file in backend:

```bash
FLASK_ENV=production
FLASK_DEBUG=False
CACHE_TIMEOUT=300
```

---

## Performance Optimization

### 1. Enable Gzip Compression (Nginx)

```nginx
gzip on;
gzip_vary on;
gzip_min_length 256;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
```

### 2. CDN for Static Assets

Consider using a CDN for:
- Map tiles
- JavaScript libraries
- CSS frameworks

### 3. Database Caching (Future)

For larger deployments, consider:
- Redis for caching
- PostgreSQL for historical data

---

## Monitoring

### Health Check Endpoint

Monitor `/api/health` endpoint:

```bash
# Simple check
curl http://your-domain.com/api/health

# Uptime monitoring services
# - UptimeRobot
# - Pingdom
# - StatusCake
```

### Logging

**Application Logs:**
```bash
# Systemd service logs
journalctl -u philearthstats -f

# Gunicorn logs
tail -f /var/log/gunicorn/error.log
```

**Web Server Logs:**
```bash
# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Apache
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
```

---

## Backup

### Backend Code
```bash
git clone https://github.com/your-repo/philearthstats.git
```

### Configuration Files
```bash
# Backup important configs
tar -czf philearthstats-config-backup.tar.gz \
  /etc/nginx/sites-available/philearthstats \
  /etc/systemd/system/philearthstats.service \
  /opt/philearthstats/backend/.env
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer** (Nginx/HAProxy)
2. **Multiple Backend Instances**
3. **Shared Cache** (Redis)

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize Gunicorn workers: `workers = (2 * CPU_CORES) + 1`

---

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Firewall configured (allow only 80, 443, SSH)
- [ ] SSH key-based authentication
- [ ] Regular security updates
- [ ] Environment variables not committed to Git
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Monitoring and alerting set up

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
journalctl -u philearthstats -n 50

# Test Flask directly
cd backend
source venv/bin/activate
python app.py
```

### Frontend not loading
```bash
# Rebuild
cd frontend
rm -rf node_modules dist
npm install
npm run build

# Check Nginx config
sudo nginx -t
```

### API errors
```bash
# Test API directly
curl http://localhost:5000/api/health
curl http://localhost:5000/api/earthquakes/recent

# Check external API access
curl https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson
```

---

## Support

For deployment issues:
1. Check application logs
2. Verify all services are running
3. Test API endpoints manually
4. Review Nginx/Apache configurations

---

**Happy Deploying! 🚀**
