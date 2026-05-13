# Vessel Rating System - REST API Documentation

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the API server
python api_server.py
```

The API will be available at: **http://localhost:8000**

### 2. Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. Test the API

```bash
# Using curl
curl http://localhost:8000/api/v1/health

# Or run the examples
python api_examples.py
```

---

## 📋 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

---

## 1. Health Check

**Endpoint**: `GET /health`

**Description**: Check API health status and database connectivity

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-04-22T10:30:00.000Z",
  "components": {
    "database": "connected",
    "api": "operational",
    "scoring_engine": "ready"
  }
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/health
```

---

## 2. Analyze Single Vessel

**Endpoint**: `POST /analyze`

**Description**: Analyze a single vessel and get comprehensive risk rating

**Request Body**:
```json
{
  "vessel_name": "Ever Given",
  "imo_number": "9860910"
}
```

**Response**:
```json
{
  "vessel_name": "Ever Given",
  "imo_number": "9860910",
  "analysis_date": "2024-04-22T10:30:00.000Z",
  "final_rating": 6.2,
  "band_rating": 6,
  "risk_level": "High",
  "module_scores": [
    {
      "module_name": "General Information",
      "score": 7.0,
      "weight": 10,
      "weighted_score": 0.7,
      "details": {...}
    },
    // ... more modules
  ],
  "critical_alerts": [
    "Vessel has recent detention history"
  ],
  "recommendation": "Require enhanced risk monitoring",
  "processing_time_seconds": 2.45
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_name": "Ever Given",
    "imo_number": "9860910"
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "vessel_name": "Ever Given",
        "imo_number": "9860910"
    }
)
data = response.json()
print(f"Rating: {data['final_rating']}/9")
print(f"Risk Level: {data['risk_level']}")
```

---

## 3. Batch Analysis

**Endpoint**: `POST /batch-analyze`

**Description**: Analyze multiple vessels in a single request

**Request Body**:
```json
{
  "vessels": [
    {"vessel_name": "Ever Given", "imo_number": "9860910"},
    {"vessel_name": "MSC Zoe", "imo_number": "7904881"},
    {"vessel_name": "OOCL Hong Kong", "imo_number": "9711519"}
  ]
}
```

**Response**:
```json
{
  "total_vessels": 3,
  "successful": 3,
  "failed": 0,
  "processing_time_seconds": 7.85,
  "results": [
    {
      "vessel_name": "Ever Given",
      "final_rating": 6.2,
      "risk_level": "High",
      ...
    },
    // ... more results
  ],
  "errors": null,
  "summary": {
    "average_rating": 5.8,
    "high_risk_count": 2,
    "medium_risk_count": 1,
    "low_risk_count": 0
  }
}
```

**Example**:
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

---

## 4. Get Vessel History

**Endpoint**: `GET /history/{imo_number}`

**Description**: Get analysis history for a specific vessel

**Path Parameters**:
- `imo_number` (string, required): IMO number of the vessel

**Response**:
```json
{
  "vessel_name": "Ever Given",
  "imo_number": "9860910",
  "total_analyses": 5,
  "latest_analysis_date": "2024-04-22T10:30:00.000Z",
  "latest_rating": 6.2,
  "ratings_history": [
    {
      "date": "2024-04-20T08:15:00.000Z",
      "rating": 6.0,
      "band": 6,
      "risk_level": "High"
    },
    {
      "date": "2024-04-22T10:30:00.000Z",
      "rating": 6.2,
      "band": 6,
      "risk_level": "High"
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/history/9860910
```

---

## 5. Get Scoring Modules Info

**Endpoint**: `GET /modules`

**Description**: Get information about all scoring modules, their weights, and criteria

**Response**:
```json
{
  "modules": [
    {
      "id": 1,
      "name": "General Information",
      "weight": 10,
      "description": "Vessel class, age, flag state, port state control history",
      "factors": ["vessel_class", "age", "flag_state", "psc_history"]
    },
    {
      "id": 2,
      "name": "Ownership Information",
      "weight": 20,
      "description": "Beneficial owners, company history, beneficial owner sanctions",
      "factors": ["owner_profile", "company_sanctions", "ownership_changes"]
    },
    {
      "id": 3,
      "name": "AIS Information",
      "weight": 15,
      "description": "Automatic Identification System signal patterns and anomalies",
      "factors": ["ais_signal_strength", "route_anomalies", "spoofing_detection"]
    },
    {
      "id": 4,
      "name": "Risk & Compliance",
      "weight": 30,
      "description": "Sanctions status, compliance violations, incident history (CRITICAL)",
      "factors": ["sanctions_status", "violations", "incident_history"]
    },
    {
      "id": 5,
      "name": "Environmental & Voyage",
      "weight": 15,
      "description": "Route information, environmental compliance, cargo type",
      "factors": ["route_risk", "environmental_violations", "cargo_hazard_level"]
    },
    {
      "id": 6,
      "name": "Legal & Documentation",
      "weight": 10,
      "description": "Certification status, insurance, documentation completeness",
      "factors": ["certification_status", "insurance_valid", "doc_completeness"]
    }
  ],
  "total_weight": 100,
  "rating_scale": {
    "min": 0,
    "max": 9,
    "type": "band rating",
    "risk_levels": [
      "Minimal (0)",
      "Low (1-2)",
      "Medium (3-5)",
      "High (6-7)",
      "Critical (8-9)"
    ]
  }
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/modules
```

---

## 6. Get System Statistics

**Endpoint**: `GET /stats`

**Description**: Get system-wide statistics

**Response**:
```json
{
  "total_vessels_analyzed": 42,
  "total_analyses": 156,
  "average_rating": 5.3,
  "risk_distribution": {
    "critical": 8,
    "high": 24,
    "medium": 62,
    "low": 54,
    "minimal": 8
  },
  "last_analysis": "2024-04-22T10:30:00.000Z"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/stats
```

---

## 🔄 Response Format

All successful responses return:
```json
{
  "data": {...},
  "status": "success",
  "timestamp": "ISO-8601 timestamp"
}
```

Error responses return:
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "status": "error",
  "timestamp": "ISO-8601 timestamp"
}
```

---

## 📊 Rating Scale

The system uses a **0-9 band rating**:

| Band | Risk Level | Description |
|------|-----------|-------------|
| 0 | Minimal | Very low risk, excellent compliance |
| 1-2 | Low | Low risk, good compliance record |
| 3-5 | Medium | Moderate risk, acceptable standards |
| 6-7 | High | High risk, concerning issues |
| 8-9 | Critical | Critical risk, immediate action required |

---

## ⚙️ Module Weights

The final rating is calculated using weighted scores from 6 modules:

| Module | Weight | Criticality |
|--------|--------|-------------|
| General Information | 10% | Standard |
| Ownership Information | 20% | Important |
| AIS Information | 15% | Important |
| **Risk & Compliance** | **30%** | **CRITICAL** |
| Environmental & Voyage | 15% | Important |
| Legal & Documentation | 10% | Standard |

---

## 🔐 Authentication

Currently, the API has **no authentication** (open access). To add authentication:

1. Add to `api_server.py`:
```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@app.get("/protected", dependencies=[Depends(security)])
async def protected_route():
    return {"message": "Protected endpoint"}
```

2. Or use API keys:
```python
from fastapi import Header, HTTPException

@app.get("/protected")
async def protected_route(x_api_key: str = Header(None)):
    if x_api_key != "your_secret_key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return {"message": "Protected endpoint"}
```

---

## 🚀 Deployment

### Local Development
```bash
python api_server.py
```

### Production (using Gunicorn + Uvicorn)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

### Docker
```bash
docker build -t vessel-rating-api .
docker run -p 8000:8000 vessel-rating-api
```

### Environment Variables
Create `.env` file:
```env
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///./db/vessel_ratings.db
LOG_LEVEL=INFO
```

---

## 📝 Examples

### Example 1: Simple Python Client
```python
import requests
import json

API_URL = "http://localhost:8000/api/v1"

# Analyze a vessel
response = requests.post(f"{API_URL}/analyze", json={
    "vessel_name": "Ever Given",
    "imo_number": "9860910"
})

if response.status_code == 200:
    result = response.json()
    print(f"Final Rating: {result['final_rating']}/9")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Processing Time: {result['processing_time_seconds']}s")
else:
    print(f"Error: {response.status_code}")
```

### Example 2: JavaScript/Fetch
```javascript
const API_URL = "http://localhost:8000/api/v1";

async function analyzeVessel(vesselName, imoNumber) {
    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vessel_name: vesselName,
                imo_number: imoNumber
            })
        });
        
        const data = await response.json();
        console.log(`Rating: ${data.final_rating}/9`);
        console.log(`Risk Level: ${data.risk_level}`);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

analyzeVessel("Ever Given", "9860910");
```

### Example 3: cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze vessel
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"vessel_name":"Ever Given","imo_number":"9860910"}'

# Get history
curl http://localhost:8000/api/v1/history/9860910

# Get statistics
curl http://localhost:8000/api/v1/stats
```

---

## 🐛 Error Handling

### Common Errors

**400 Bad Request** - Invalid input
```json
{
  "error": "Validation Error",
  "message": "imo_number: ensure this value has at least 5 characters"
}
```

**404 Not Found** - Vessel not found in history
```json
{
  "error": "Not Found",
  "message": "No vessel found with IMO: 9999999"
}
```

**500 Internal Server Error** - Server error
```json
{
  "error": "Internal Server Error",
  "message": "Database connection failed"
}
```

---

## 📚 Running Examples

```bash
# Run interactive examples with menu
python api_examples.py

# Run specific example
python -c "from api_examples import example_2_single_analysis; example_2_single_analysis()"
```

---

## 🔗 Related Documentation

- [README.md](README.md) - System overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [GETTING_STARTED.md](GETTING_STARTED.md) - Getting started guide

---

## 📞 Support

For issues or questions:
1. Check the [interactive API docs](http://localhost:8000/docs)
2. Review example scripts: `api_examples.py`
3. Check logs: `logs/vessel_rating.log`
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

**Last Updated**: April 2024  
**API Version**: 1.0.0
