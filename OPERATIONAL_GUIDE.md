# Hashtag Sentiment Analyzer - Operational Guide

## 📋 Document Overview
**Document Type**: Operational Guide  
**Version**: 6.0  
**Date**: August 10, 2025  
**Status**: Current Production Guide  

---

## 🎯 Purpose & Scope

This operational guide provides comprehensive instructions for deploying, monitoring, maintaining, and troubleshooting the Hashtag Sentiment Analyzer application in production environments.

### Target Audience
- **DevOps Engineers**: Deployment and infrastructure management
- **System Administrators**: Server maintenance and monitoring
- **Support Engineers**: Issue resolution and troubleshooting
- **Development Team**: Bug fixes and feature updates

---

## 🏗️ System Architecture Overview

```
Internet
    │
    ├── Frontend (React) ────────── http://localhost:3000
    │   ├── Static Assets
    │   ├── UI Components  
    │   └── API Client
    │
    ├── Backend (Flask) ─────────── http://localhost:5000
    │   ├── REST API Endpoints
    │   ├── Data Collection Engine
    │   └── Processing Logic
    │
    └── External Services
        ├── Twitter API v2 ───────── api.twitter.com
        ├── Nitter Instances ─────── nitter.net, etc.
        ├── Chrome WebDriver ─────── Local installation
        └── Alternative Sources ───── threadreaderapp.com, etc.
```

---

## 🚀 Deployment Procedures

### Pre-deployment Checklist

#### Environment Requirements
- [ ] **Python 3.9+** installed
- [ ] **Node.js 18+** installed  
- [ ] **Chrome Browser** installed
- [ ] **ChromeDriver** in system PATH
- [ ] **Twitter API Bearer Token** available
- [ ] **Git** repository access
- [ ] **Port availability**: 3000, 5000

#### System Dependencies
```bash
# Python packages
pip install flask flask-cors tweepy python-dotenv requests beautifulsoup4 selenium

# Node.js packages  
npm install react react-dom typescript @types/react @types/react-dom

# System packages
sudo apt-get install google-chrome-stable  # Ubuntu/Debian
brew install chromedriver                   # macOS
```

### Development Deployment

#### Step 1: Repository Setup
```bash
# Clone repository
git clone <repository-url>
cd hashtag-sentiment-analyzer

# Verify directory structure
ls -la
# Expected: backend/, frontend/, README.md, *.md files
```

#### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
TWITTER_BEARER_TOKEN=your_bearer_token_here
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:3000
EOF

# Test installation
python app.py
# Expected: "Running on http://127.0.0.1:5000"
```

#### Step 3: Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Verify proxy configuration
grep -A 2 -B 2 "proxy" package.json
# Expected: "proxy": "http://localhost:5000"

# Start development server
npm start
# Expected: Opens http://localhost:3000
```

#### Step 4: Verification
```bash
# Backend health check
curl http://localhost:5000/health
# Expected: {"status": "healthy", ...}

# Frontend connectivity
curl http://localhost:3000
# Expected: HTML response

# Full system test
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"hashtag": "test", "count": 5}'
# Expected: JSON response with analysis data
```

### Production Deployment

#### Step 1: Server Preparation
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade

# Install required packages
sudo apt-get install python3 python3-pip nodejs npm nginx

# Install Chrome for headless operation
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -O chrome_version
CHROMEDRIVER_VERSION=$(cat chrome_version)
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

#### Step 2: Application Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash appuser
sudo su - appuser

# Clone and setup application
git clone <repository-url> /home/appuser/hashtag-analyzer
cd /home/appuser/hashtag-analyzer

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Production environment file
cat > .env << EOF
TWITTER_BEARER_TOKEN=${TWITTER_TOKEN}
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://yourdomain.com
EOF

# Frontend build
cd ../frontend
npm install
npm run build
```

#### Step 3: Process Management (systemd)
```bash
# Backend service
sudo tee /etc/systemd/system/hashtag-analyzer-backend.service << EOF
[Unit]
Description=Hashtag Analyzer Backend
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/home/appuser/hashtag-analyzer/backend
Environment=PATH=/home/appuser/hashtag-analyzer/backend/venv/bin
ExecStart=/home/appuser/hashtag-analyzer/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hashtag-analyzer-backend
sudo systemctl start hashtag-analyzer-backend
sudo systemctl status hashtag-analyzer-backend
```

#### Step 4: Reverse Proxy (nginx)
```bash
# Nginx configuration
sudo tee /etc/nginx/sites-available/hashtag-analyzer << EOF
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend (React build)
    location / {
        root /home/appuser/hashtag-analyzer/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/hashtag-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Docker Deployment

#### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}
      - FLASK_ENV=production
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

#### Dockerfiles
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1) \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O /tmp/version \
    && CHROMEDRIVER_VERSION=$(cat /tmp/version) \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

---

## 📊 Monitoring & Logging

### Health Monitoring

#### Automated Health Checks
```bash
#!/bin/bash
# health-check.sh

# Backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ $BACKEND_STATUS != "200" ]; then
    echo "ALERT: Backend health check failed - HTTP $BACKEND_STATUS"
    # Send alert notification
fi

# Frontend availability
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ $FRONTEND_STATUS != "200" ]; then
    echo "ALERT: Frontend availability check failed - HTTP $FRONTEND_STATUS"
fi

# Twitter API connectivity
API_TEST=$(curl -s -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"hashtag": "test", "count": 1, "data_source": "api"}' \
  | grep -c "success")
if [ $API_TEST -eq 0 ]; then
    echo "WARNING: Twitter API integration may have issues"
fi

# Chrome/Selenium availability
CHROME_VERSION=$(google-chrome --version 2>/dev/null || echo "NOT_INSTALLED")
CHROMEDRIVER_VERSION=$(chromedriver --version 2>/dev/null || echo "NOT_INSTALLED")
echo "INFO: Chrome: $CHROME_VERSION"
echo "INFO: ChromeDriver: $CHROMEDRIVER_VERSION"
```

#### Cron Job Setup
```bash
# Add to crontab (crontab -e)
*/5 * * * * /home/appuser/health-check.sh >> /var/log/hashtag-analyzer/health.log 2>&1
0 0 * * * find /var/log/hashtag-analyzer/ -name "*.log" -mtime +7 -delete
```

### Application Logging

#### Log Configuration
```python
# backend/app.py - Add logging configuration
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    # Production logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/hashtag-analyzer.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Hashtag Analyzer startup')
```

#### Log Analysis Commands
```bash
# Error analysis
tail -f /var/log/hashtag-analyzer/backend.log | grep ERROR

# Request patterns
grep "POST /api/analyze" /var/log/hashtag-analyzer/backend.log | \
  awk '{print $4}' | sort | uniq -c | sort -nr

# Performance monitoring
grep "SUCCESS:" /var/log/hashtag-analyzer/backend.log | \
  grep -o "tweets.*seconds" | \
  awk '{print $3}' | sort -n

# Data source usage
grep "data_source" /var/log/hashtag-analyzer/backend.log | \
  grep -o "web_scraping\|twitter_api" | sort | uniq -c
```

### Performance Metrics

#### Key Performance Indicators (KPIs)
```bash
# Response time monitoring
curl -w "@curl-format.txt" -s -o /dev/null \
  -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"hashtag": "python", "count": 10}'

# curl-format.txt content:
#      time_namelookup:  %{time_namelookup}s\n
#         time_connect:  %{time_connect}s\n
#      time_appconnect:  %{time_appconnect}s\n
#     time_pretransfer:  %{time_pretransfer}s\n
#        time_redirect:  %{time_redirect}s\n
#   time_starttransfer:  %{time_starttransfer}s\n
#                     ----------\n
#           time_total:  %{time_total}s\n
```

#### System Resource Monitoring
```bash
# Memory usage
ps aux | grep -E "(python|node|nginx)" | awk '{sum+=$6} END {print "Total Memory: " sum/1024 " MB"}'

# CPU usage
top -b -n1 | grep -E "(python|node|nginx)" | awk '{sum+=$9} END {print "Total CPU: " sum "%"}'

# Disk usage
du -sh /home/appuser/hashtag-analyzer/
df -h /var/log/hashtag-analyzer/

# Network connections
netstat -tulpn | grep -E ":(3000|5000)"
```

---

## 🔧 Maintenance Procedures

### Daily Maintenance

#### Morning Health Check
```bash
#!/bin/bash
# daily-check.sh

echo "=== Daily Health Check - $(date) ==="

# Service status
systemctl status hashtag-analyzer-backend
systemctl status nginx

# Log analysis
echo "Last 24h error count:"
grep -c "ERROR" /var/log/hashtag-analyzer/backend.log

echo "Last 24h request count:"
grep -c "POST /api/analyze" /var/log/hashtag-analyzer/backend.log

# Disk space
echo "Disk usage:"
df -h /

# Memory usage
echo "Memory usage:"
free -h

# Network connectivity
echo "External services check:"
curl -s -o /dev/null -w "Twitter API: %{http_code}\n" "https://api.twitter.com/2/tweets/search/recent?query=test"
curl -s -o /dev/null -w "Nitter.net: %{http_code}\n" "https://nitter.net"
```

### Weekly Maintenance

#### Log Rotation and Cleanup
```bash
#!/bin/bash
# weekly-maintenance.sh

# Rotate logs
logrotate -f /etc/logrotate.d/hashtag-analyzer

# Clean old temporary files
find /tmp -name "chrome*" -mtime +7 -delete
find /tmp -name "selenium*" -mtime +7 -delete

# Update Nitter instance list
curl -s "https://api.github.com/repos/zedeus/nitter/wiki" | \
  grep -o "https://[^\"]*nitter[^\"]*" | \
  sort | uniq > /tmp/nitter-instances.txt

# System updates (if approved)
# sudo apt-get update && sudo apt-get upgrade -y

# Certificate renewal (if using SSL)
# certbot renew --quiet
```

### Monthly Maintenance

#### Performance Review
```bash
#!/bin/bash
# monthly-review.sh

echo "=== Monthly Performance Review - $(date) ==="

# Calculate average response times
grep "processing_time" /var/log/hashtag-analyzer/backend.log | \
  grep -o "[0-9.]*s" | sed 's/s//' | \
  awk '{sum+=$1; count++} END {print "Average response time: " sum/count "s"}'

# Success rate analysis
TOTAL_REQUESTS=$(grep -c "POST /api/analyze" /var/log/hashtag-analyzer/backend.log)
SUCCESS_REQUESTS=$(grep -c "success.*true" /var/log/hashtag-analyzer/backend.log)
SUCCESS_RATE=$((SUCCESS_REQUESTS * 100 / TOTAL_REQUESTS))
echo "Success rate: $SUCCESS_RATE%"

# Data source distribution
echo "Data source usage:"
grep "data_source" /var/log/hashtag-analyzer/backend.log | \
  grep -o "twitter_api\|web_scraping" | sort | uniq -c

# Popular hashtags
echo "Top 10 hashtags:"
grep "hashtag.*#" /var/log/hashtag-analyzer/backend.log | \
  grep -o "#[a-zA-Z0-9_]*" | sort | uniq -c | sort -nr | head -10
```

#### Dependency Updates
```bash
# Backend dependencies
cd /home/appuser/hashtag-analyzer/backend
source venv/bin/activate
pip list --outdated
# Review and update as needed

# Frontend dependencies
cd ../frontend
npm outdated
# Review and update as needed

# Security updates
npm audit fix
pip-audit # if available
```

---

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: Backend Not Starting
**Symptoms:**
- Service fails to start
- Port 5000 not responding
- "ImportError" or "ModuleNotFoundError"

**Diagnosis:**
```bash
# Check service status
systemctl status hashtag-analyzer-backend

# Check logs
journalctl -u hashtag-analyzer-backend -f

# Test manual startup
cd /home/appuser/hashtag-analyzer/backend
source venv/bin/activate
python app.py
```

**Solutions:**
```bash
# Missing dependencies
pip install -r requirements.txt

# Port already in use
sudo lsof -i :5000
sudo kill -9 <PID>

# Permission issues
sudo chown -R appuser:appuser /home/appuser/hashtag-analyzer
sudo chmod +x /home/appuser/hashtag-analyzer/backend/app.py

# Environment variables
cat .env
# Verify TWITTER_BEARER_TOKEN is set
```

#### Issue 2: Twitter API Failures
**Symptoms:**
- All requests falling back to web scraping
- "401 Unauthorized" errors
- "429 Too Many Requests" errors

**Diagnosis:**
```bash
# Test API directly
curl -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" \
  "https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10"

# Check rate limits
grep "429\|rate limit" /var/log/hashtag-analyzer/backend.log
```

**Solutions:**
```bash
# Invalid token
# 1. Verify token in Twitter Developer Portal
# 2. Update .env file with correct token
# 3. Restart backend service

# Rate limiting
# 1. Reduce request frequency
# 2. Implement request queuing
# 3. Monitor usage in Twitter Developer Portal

# API changes
# 1. Check Twitter API v2 documentation
# 2. Update tweepy library if needed
pip install --upgrade tweepy
```

#### Issue 3: Web Scraping Failures
**Symptoms:**
- "No tweets found" for popular hashtags
- ChromeDriver errors
- Network timeout errors

**Diagnosis:**
```bash
# Test Chrome installation
google-chrome --version
chromedriver --version

# Test manual scraping
curl -s "https://nitter.net/search?q=%23test"

# Check Selenium logs
grep -i "selenium\|chrome" /var/log/hashtag-analyzer/backend.log
```

**Solutions:**
```bash
# Chrome/ChromeDriver mismatch
# Update ChromeDriver to match Chrome version
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}

# Network issues
# Check firewall rules
sudo ufw status
# Test external connectivity
curl -s -I "https://nitter.net"

# Update Nitter instances
# Many Nitter instances go offline - update the list regularly
```

#### Issue 4: Frontend Not Loading
**Symptoms:**
- Blank page or loading spinner
- JavaScript errors in browser console
- Failed API requests

**Diagnosis:**
```bash
# Check nginx status
sudo systemctl status nginx

# Check frontend build
ls -la /home/appuser/hashtag-analyzer/frontend/build/

# Test API connectivity
curl http://localhost:5000/health

# Check browser console for errors
# Open Developer Tools > Console
```

**Solutions:**
```bash
# Rebuild frontend
cd /home/appuser/hashtag-analyzer/frontend
npm run build

# Fix nginx configuration
sudo nginx -t
sudo systemctl reload nginx

# CORS issues
# Update CORS_ORIGINS in backend .env
# Restart backend service

# Proxy issues
# Check package.json proxy setting
# Should be "proxy": "http://localhost:5000"
```

### Emergency Procedures

#### Service Recovery
```bash
# Complete service restart
sudo systemctl stop hashtag-analyzer-backend
sudo systemctl stop nginx
sleep 5
sudo systemctl start hashtag-analyzer-backend
sudo systemctl start nginx

# Verify recovery
curl http://localhost:5000/health
curl http://localhost:3000
```

#### Data Loss Prevention
```bash
# Backup configuration
cp /home/appuser/hashtag-analyzer/backend/.env /backup/
cp /etc/nginx/sites-available/hashtag-analyzer /backup/
cp /etc/systemd/system/hashtag-analyzer-backend.service /backup/

# Log backup
tar -czf /backup/logs-$(date +%Y%m%d).tar.gz /var/log/hashtag-analyzer/
```

#### Rollback Procedure
```bash
# Stop services
sudo systemctl stop hashtag-analyzer-backend
sudo systemctl stop nginx

# Restore from backup
cd /home/appuser/hashtag-analyzer
git checkout <previous-stable-commit>

# Rebuild if necessary
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install && npm run build

# Restart services
sudo systemctl start hashtag-analyzer-backend
sudo systemctl start nginx
```

---

## 📈 Performance Optimization

### Backend Optimization

#### Python Application
```python
# Add to app.py for production
from werkzeug.middleware.profiler import ProfilerMiddleware

if app.config.get('PROFILE'):
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

# Implement caching
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_twitter_request(hashtag, count, timestamp):
    # Cache results for 5 minutes
    return twitter_service.fetch_tweets(hashtag, count)

def get_cached_tweets(hashtag, count):
    # 5-minute cache
    timestamp = int(time.time() / 300) * 300
    return cached_twitter_request(hashtag, count, timestamp)
```

#### Database Optimization (Future)
```sql
-- If adding database later
CREATE INDEX idx_tweets_hashtag_created ON tweets(hashtag, created_at);
CREATE INDEX idx_analysis_timestamp ON analyses(created_at);

-- Partitioning for large datasets
PARTITION BY RANGE (created_at);
```

### Frontend Optimization

#### React Performance
```javascript
// Implement component memoization
import React, { memo, useMemo, useCallback } from 'react';

const TweetCard = memo(({ tweet }) => {
  const formattedDate = useMemo(
    () => new Date(tweet.created_at).toLocaleString(),
    [tweet.created_at]
  );
  
  return (
    <div className="tweet-card">
      {/* Tweet content */}
    </div>
  );
});

// Implement virtual scrolling for large tweet lists
import { FixedSizeList as List } from 'react-window';

const TweetList = ({ tweets }) => {
  const Row = useCallback(({ index, style }) => (
    <div style={style}>
      <TweetCard tweet={tweets[index]} />
    </div>
  ), [tweets]);

  return (
    <List
      height={600}
      itemCount={tweets.length}
      itemSize={120}
    >
      {Row}
    </List>
  );
};
```

#### Bundle Optimization
```bash
# Analyze bundle size
npm install --save-dev webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js

# Code splitting
# Implement lazy loading for routes
const TweetsPage = React.lazy(() => import('./TweetsPage'));

# Preload critical resources
<link rel="preload" href="/api/health" as="fetch" crossorigin>
```

### Infrastructure Optimization

#### nginx Configuration
```nginx
# /etc/nginx/sites-available/hashtag-analyzer
server {
    listen 80;
    server_name yourdomain.com;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;
    
    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    
    location /api/ {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_cache_valid 200 5m;
        proxy_cache_key "$request_uri";
    }
}
```

#### Load Balancing (Multi-instance)
```bash
# HAProxy configuration
backend hashtag_backend
    balance roundrobin
    server backend1 127.0.0.1:5001 check
    server backend2 127.0.0.1:5002 check
    server backend3 127.0.0.1:5003 check

# Multiple Gunicorn instances
gunicorn -w 4 -b 127.0.0.1:5001 app:app &
gunicorn -w 4 -b 127.0.0.1:5002 app:app &
gunicorn -w 4 -b 127.0.0.1:5003 app:app &
```

---

## 🔐 Security Operations

### Security Monitoring
```bash
# Monitor failed authentication attempts
grep "401\|403\|Unauthorized" /var/log/hashtag-analyzer/backend.log

# Check for suspicious patterns
grep -E "(script|SELECT|DROP|INSERT)" /var/log/hashtag-analyzer/backend.log

# Monitor resource usage spikes
sar -u 1 5  # CPU usage
sar -r 1 5  # Memory usage
```

### Security Updates
```bash
#!/bin/bash
# security-update.sh

# System security updates
sudo apt-get update
sudo apt-get upgrade -y

# Python security updates
pip install --upgrade pip
pip-audit --fix

# Node.js security updates
npm audit fix

# SSL certificate renewal
certbot renew --dry-run
```

### Backup Procedures
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/hashtag-analyzer/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Application files
tar -czf $BACKUP_DIR/application.tar.gz /home/appuser/hashtag-analyzer/

# Configuration files
cp /home/appuser/hashtag-analyzer/backend/.env $BACKUP_DIR/
cp /etc/nginx/sites-available/hashtag-analyzer $BACKUP_DIR/
cp /etc/systemd/system/hashtag-analyzer-backend.service $BACKUP_DIR/

# Logs (last 7 days)
find /var/log/hashtag-analyzer -name "*.log" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

# Compress final backup
tar -czf "/backup/hashtag-analyzer-$(date +%Y%m%d).tar.gz" $BACKUP_DIR/
rm -rf $BACKUP_DIR

# Upload to cloud storage (configure as needed)
# aws s3 cp "/backup/hashtag-analyzer-$(date +%Y%m%d).tar.gz" s3://your-bucket/
```

---

## 📞 Support & Escalation

### Support Tiers

#### Tier 1: Basic Issues
- **Scope**: User interface issues, basic functionality questions
- **Response Time**: 4 hours during business hours
- **Resolution**: Self-service documentation, basic troubleshooting

#### Tier 2: Technical Issues  
- **Scope**: API failures, performance issues, configuration problems
- **Response Time**: 2 hours during business hours
- **Resolution**: Advanced troubleshooting, configuration changes

#### Tier 3: Critical Issues
- **Scope**: Service outages, security incidents, data corruption
- **Response Time**: 30 minutes 24/7
- **Resolution**: Emergency procedures, development team involvement

### Contact Information

#### Development Team
- **Lead Developer**: lead-dev@company.com
- **DevOps Engineer**: devops@company.com  
- **On-call**: +1-555-0123 (24/7 critical issues)

#### External Support
- **Twitter API Support**: https://twittercommunity.com/
- **Chrome/Selenium Issues**: https://selenium-python.readthedocs.io/
- **Infrastructure Provider**: [Your cloud provider support]

### Incident Response

#### Severity Levels
1. **Critical (S1)**: Complete service outage affecting all users
2. **High (S2)**: Major functionality impaired, affecting >50% users  
3. **Medium (S3)**: Minor functionality issues, workarounds available
4. **Low (S4)**: Cosmetic issues, feature requests

#### Response Procedures
```bash
# Incident declaration
echo "INCIDENT: $(date) - Description: $DESCRIPTION" >> /var/log/incidents.log

# Immediate response
./emergency-restore.sh

# Communication
# Notify stakeholders via configured channels
# Update status page if available

# Investigation
./collect-diagnostics.sh > /tmp/incident-$(date +%Y%m%d-%H%M).log

# Resolution tracking
# Document steps taken
# Verify service restoration
# Conduct post-incident review
```

---

## 📋 Checklists

### Pre-Deployment Checklist
- [ ] Environment variables configured
- [ ] Dependencies installed and updated
- [ ] Security configurations applied  
- [ ] Backup procedures tested
- [ ] Monitoring systems configured
- [ ] Documentation updated
- [ ] Team notified of deployment

### Post-Deployment Checklist
- [ ] Health checks passing
- [ ] Performance metrics within acceptable range
- [ ] Error rates below threshold
- [ ] User acceptance testing completed
- [ ] Rollback plan prepared and tested
- [ ] Support team briefed on changes

### Monthly Review Checklist
- [ ] Performance metrics analyzed
- [ ] Security updates applied
- [ ] Dependencies updated
- [ ] Backup integrity verified
- [ ] Disaster recovery plan tested
- [ ] Documentation reviewed and updated
- [ ] Capacity planning reviewed

---

*Document Version: 6.0*  
*Last Updated: August 10, 2025*  
*Next Review Date: November 10, 2025*