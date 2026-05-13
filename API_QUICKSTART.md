# REST API Setup Guide

## 🚀 Quick Start - 3 Steps

### Step 1: Install Updated Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi==0.104.1` - Web framework for REST API
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.4.2` - Data validation

### Step 2: Start the API Server

Choose one of these options:

**Option A: Using Quickstart Script (Recommended)**
```bash
python quickstart.py --api
```

**Option B: Direct Command**
```bash
python api_server.py
```

**Option C: Using Uvicorn directly**
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Access the API

The API will start on `http://localhost:8000`

**Access points:**
- 📚 **Interactive Docs**: http://localhost:8000/docs
- 📖 **Alternative Docs**: http://localhost:8000/redoc
- 🔌 **API Base**: http://localhost:8000/api/v1

---

## 📊 Available Endpoints

### Health & Info
- `GET /health` - Check API status
- `GET /` - API information
- `GET /modules` - Get module information
- `GET /stats` - System statistics

### Analysis
- `POST /analyze` - Analyze single vessel
- `POST /batch-analyze` - Analyze multiple vessels
- `GET /history/{imo_number}` - Get vessel analysis history

---

## 🧪 Test the API

### Method 1: Using Interactive Swagger UI
1. Go to: http://localhost:8000/docs
2. Click on endpoint
3. Click "Try it out"
4. Enter values
5. Click "Execute"

### Method 2: Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze a vessel
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_name": "Ever Given",
    "imo_number": "9860910"
  }'

# Get statistics
curl http://localhost:8000/api/v1/stats
```

### Method 3: Using Python

```python
import requests

# Analyze vessel
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "vessel_name": "Ever Given",
        "imo_number": "9860910"
    }
)

result = response.json()
print(f"Rating: {result['final_rating']}/9")
print(f"Risk: {result['risk_level']}")
```

### Method 4: Using API Examples Script

```bash
python api_examples.py
```

This runs an interactive menu with:
1. Health Check
2. Single Vessel Analysis
3. Batch Analysis
4. Module Information
5. System Statistics
6. Vessel History
7. Error Handling

---

## 📋 Common API Usage Examples

### Example 1: Quick Status Check
```bash
curl http://localhost:8000/api/v1/health
```

### Example 2: Analyze One Vessel
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_name": "MSC Zoe",
    "imo_number": "7904881"
  }'
```

### Example 3: Analyze Multiple Vessels
```bash
curl -X POST http://localhost:8000/api/v1/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vessels": [
      {"vessel_name": "Ever Given", "imo_number": "9860910"},
      {"vessel_name": "MSC Zoe", "imo_number": "7904881"}
    ]
  }'
```

### Example 4: Get Vessel History
```bash
curl http://localhost:8000/api/v1/history/9860910
```

### Example 5: See All Modules
```bash
curl http://localhost:8000/api/v1/modules
```

---

## 🔧 Configuration

### Environment Variables (Optional)

Create `.env` file in project root:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./db/vessel_ratings.db

# Logging
LOG_LEVEL=INFO
```

### Change Port

To run on different port:

```bash
# Using Uvicorn
uvicorn api_server:app --port 9000

# Using quickstart
python api_server.py  # Edit port in api_server.py
```

---

## 📚 Full Documentation

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

Topics covered:
- All endpoints with examples
- Request/response models
- Error handling
- Authentication (optional setup)
- Deployment guides
- JavaScript/Python client examples
- Docker deployment

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"

**Solution:** Port 8000 is already in use. Either:
1. Stop the other process
2. Run on different port:
```bash
uvicorn api_server:app --port 9000
```

### Error: "Database connection failed"

**Solution:**
```bash
python quickstart.py --init
```

### API responds but endpoints return 500 error

**Solution:** Check logs and ensure database is initialized:
```bash
python quickstart.py --init
```

---

## 🚀 Running Both UI and API

You can run both simultaneously in separate terminals:

**Terminal 1 - Streamlit UI:**
```bash
python quickstart.py
```

**Terminal 2 - REST API:**
```bash
python quickstart.py --api
```

Now you have:
- 🖥️ Web UI at: http://localhost:8501
- 🔌 REST API at: http://localhost:8000

---

## 📖 Next Steps

1. **Try the interactive docs**: http://localhost:8000/docs
2. **Run examples**: `python api_examples.py`
3. **Read full docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. **Check deployment options**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔗 Related Files

- `api_server.py` - Main API server
- `api/routes.py` - API endpoints
- `api_examples.py` - Usage examples
- `API_DOCUMENTATION.md` - Full documentation
- `requirements.txt` - Dependencies

---

**Last Updated**: April 2024  
**Vessel Rating System v1.0.0**
