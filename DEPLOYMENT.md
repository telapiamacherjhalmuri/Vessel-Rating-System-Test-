# Vessel Rating System - Deployment & Configuration Guide

## 🚀 Deployment Overview

This guide covers deployment scenarios for the Vessel Rating System.

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (for version control)

### 5-Minute Setup

```bash
# 1. Navigate to project
cd e:\Vessel_Rating_System

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Run quickstart
python quickstart.py

# 4. Open browser
# Browser will automatically open to http://localhost:8501
```

That's it! The system handles the rest.

---

## Advanced Setup (Production)

### Step 1: Environment Configuration

Create `.env` file in project root:

```env
# Flask/Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vessel_ratings
# Or SQLite:
# DATABASE_URL=sqlite:///./db/vessel_ratings.db

# API Keys (get from respective providers)
AIS_API_KEY=your_marinetraffic_key
WEATHER_API_KEY=your_openweather_key
SANCTIONS_API_KEY=your_sanctions_api_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/vessel_rating.log

# Feature Flags
ENABLE_AI_ANOMALY=false
ENABLE_PREDICTIVE_SCORING=false
CACHE_ENABLED=true
CACHE_TTL=3600

# Email Alerts (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Step 2: Database Setup

#### Using SQLite (Default)
```bash
python -c "from db.models import init_db; init_db()"
```

#### Using PostgreSQL (Recommended for Production)

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE vessel_ratings;
CREATE USER vrs_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE vessel_ratings TO vrs_user;
```

3. Update `.env`:
```
DATABASE_URL=postgresql://vrs_user:secure_password@localhost:5432/vessel_ratings
```

4. Initialize:
```bash
python -c "from db.models import init_db; init_db('postgresql://...')"
```

### Step 3: API Integration Setup

#### Option A: Use Demo Mode (No API Keys)
System runs with simulated data - perfect for testing

```python
# Already configured in api_integration/providers.py
# Just run: python quickstart.py
```

#### Option B: Connect Real APIs

Edit `api_integration/providers.py`:

**AIS Data:**
```python
class AISProvider:
    def get_ais_data(self, vessel_name, imo_number):
        response = requests.get(
            f"{API_CONFIG['AIS_API']['endpoint']}/v1/vessels/{imo_number}",
            headers={"Authorization": f"Bearer {os.getenv('AIS_API_KEY')}"},
            timeout=10
        )
        return response.json()
```

**Sanctions Check:**
```python
class SanctionsProvider:
    def check_sanctions(self, vessel_name, imo_number):
        # Integrate with OFAC API
        # https://www.treasury.gov/ofac/
        pass
```

### Step 4: Deploy to Server

#### Option A: Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy:
```
GitHub Repo: your_repo/Vessel_Rating_System
Main file: app/main.py
```

#### Option B: Self-Hosted (VPS/AWS/Azure)

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3.10 python3-pip git postgresql
```

2. Clone repository:
```bash
git clone your_repo vessel_rating
cd vessel_rating
```

3. Setup:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Create systemd service:
```ini
# /etc/systemd/system/vessel-rating.service
[Unit]
Description=Vessel Rating System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/www-data/vessel_rating
Environment="PATH=/home/www-data/vessel_rating/venv/bin"
ExecStart=/home/www-data/vessel_rating/venv/bin/streamlit run app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Enable and start:
```bash
sudo systemctl enable vessel-rating
sudo systemctl start vessel-rating
sudo systemctl status vessel-rating
```

#### Option C: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t vessel-rating .
docker run -p 8501:8501 -e DATABASE_URL=postgresql://... vessel-rating
```

### Step 5: Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name vessel-rating.example.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Configuration Tuning

### Performance Optimization

In `config.py`:

```python
# Enable caching for faster responses
FEATURES["CACHE_RESULTS"] = True
CACHE_TTL = 3600  # 1 hour

# Database optimization
DB_CONFIG = {
    "pool_size": 20,        # Increase for more concurrent users
    "max_overflow": 30,     # Overflow connections
    "pool_recycle": 3600,   # Recycle connections
}

# Streamlit optimization
st.set_page_config(
    page_title="Vessel Rating System",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.session_state.clear()  # Clear memory between reruns
```

### Security Hardening

1. **HTTPS Only**:
```bash
# Streamlit config
streamlit_config.toml:
[server]
sslKeyFile = "/path/to/key.pem"
sslCertFile = "/path/to/cert.pem"
```

2. **Authentication**:
```python
# Add to app/main.py
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials={...},
    cookie_name="vessel_rating",
    key="secret_key",
    cookie_expiry_days=1
)

name, authentication_status = authenticator.login()
if authentication_status is False:
    st.error("Invalid credentials")
    st.stop()
```

3. **API Key Security**:
```python
# Never commit keys to git
# Use environment variables
API_KEY = os.getenv("AIS_API_KEY")
if not API_KEY:
    raise ValueError("AIS_API_KEY not set")
```

### Scaling Considerations

For 100+ concurrent users:

1. **Use PostgreSQL** (not SQLite)
2. **Implement caching layer** (Redis)
3. **Load balancing** (Nginx, HAProxy)
4. **Horizontal scaling** (multiple Streamlit instances)
5. **CDN for static assets** (CloudFlare, AWS CloudFront)

```python
# Redis caching example
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_vessel_data_cached(imo):
    cached = cache.get(f"vessel:{imo}")
    if cached:
        return json.loads(cached)
    
    data = api.fetch_all_vessel_data(imo)
    cache.setex(f"vessel:{imo}", 3600, json.dumps(data))
    return data
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check application status
curl http://localhost:8501 -I

# Check database connectivity
python -c "from db.models import get_session; print(get_session())"

# Check API connectivity
python api_integration/providers.py
```

### Logging Configuration

In `config.py`:

```python
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/vessel_rating.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}
```

### Backup Strategy

```bash
# Daily database backup
0 2 * * * pg_dump vessel_ratings > /backups/vessel_ratings_$(date +%Y%m%d).sql

# Archive and compress
0 3 * * * tar -czf /backups/vessel_ratings_$(date +%Y%m%d).tar.gz /backups/*.sql
```

### Update & Maintenance

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run migrations
python -c "from db.models import init_db; init_db()"

# Restart service
sudo systemctl restart vessel-rating
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 8501 already in use | `streamlit run app/main.py --server.port 8502` |
| Database locked | Restart Streamlit, check concurrent connections |
| API timeout | Increase timeout in `config.py`, check API status |
| Memory issues | Reduce cache TTL, clear session state |
| Slow responses | Enable caching, use PostgreSQL, add indexes |

### Debug Mode

```bash
streamlit run app/main.py --logger.level=debug
```

---

## API Integrations (Real World)

### MarineTraffic (AIS)
- Cost: Free tier available, $99-999/month commercial
- Docs: https://www.marinetraffic.com/api/
- Demo: Works with key

### OpenWeather (Weather)
- Cost: Free tier available, $400/month commercial
- Docs: https://openweathermap.org/api
- Setup: `export WEATHER_API_KEY=...`

### OFAC/UN Lists (Sanctions)
- Cost: Free public access
- Source: https://www.treasury.gov/ofac/
- Update: Downloaded weekly

### Equasis (Maritime DB)
- Cost: Free registration required
- Docs: https://www.equasis.org/
- Data: Comprehensive vessel records

---

## Support & Issues

For deployment issues:

1. Check logs: `tail -f logs/vessel_rating.log`
2. Verify config: `python -c "from config import *; print(SCORING_WEIGHTS)"`
3. Test components: `python examples.py`
4. Review README.md for detailed documentation

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Avg analysis time | 5-10 seconds |
| Max concurrent users | 50+ (with PostgreSQL) |
| DB query time | <100ms (indexed) |
| API response time | 2-5 seconds |
| Memory per session | ~50MB |
| Disk per 1000 records | ~5MB |

---

**Last Updated**: April 2024
**Version**: 1.0.0
