# Decoy Status API

This Discord bot now includes a public API that allows other applications to check the decoy status without accessing Discord channels.

## API Endpoints

### GET /status
Returns the current decoy status and metadata.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ON" | "OFF" | null,
    "last_update": "2024-01-15T10:30:00",
    "last_check": "2024-01-15T10:35:00",
    "bot_online": true,
    "check_interval": 5
  },
  "api_version": "1.0",
  "timestamp": "2024-01-15T10:35:00"
}
```

### GET /health
Health check endpoint to verify the service is running.

**Response:**
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "bot_online": true,
  "last_check": "2024-01-15T10:35:00",
  "timestamp": "2024-01-15T10:35:00"
}
```

### GET /info
Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Decoy Status API",
  "version": "1.0",
  "description": "Public API for checking decoy status from Discord bot",
  "endpoints": {
    "/status": "GET - Get current decoy status",
    "/health": "GET - Health check",
    "/info": "GET - API information"
  },
  "timestamp": "2024-01-15T10:35:00"
}
```

## Usage Examples

### Python
```python
import requests

# Get decoy status
response = requests.get('https://your-railway-app.railway.app/status')
data = response.json()

if data['success']:
    status = data['data']['status']
    print(f"Decoy status: {status}")
else:
    print(f"Error: {data['error']}")
```

### JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

async function getDecoyStatus() {
    try {
        const response = await fetch('https://your-railway-app.railway.app/status');
        const data = await response.json();
        
        if (data.success) {
            console.log(`Decoy status: ${data.data.status}`);
        } else {
            console.error(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Request failed:', error);
    }
}
```

### cURL
```bash
# Get decoy status
curl https://your-railway-app.railway.app/status

# Health check
curl https://your-railway-app.railway.app/health
```

## Configuration

The API server runs on port 5000 by default. You can configure it using environment variables:

- `API_PORT`: Port for the API server (default: 5000)
- `API_HOST`: Host for the API server (default: 0.0.0.0)

## Integration with Your Apps

1. **Replace Discord channel monitoring** with API calls
2. **Poll the `/status` endpoint** periodically (every 5-10 seconds)
3. **Use `/health` endpoint** to verify the service is running
4. **Handle API errors gracefully** in your applications

## Status Values

- `"ON"`: Decoy check is in progress
- `"OFF"`: Decoy check is complete
- `null`: No recent decoy activity detected

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `404`: Endpoint not found
- `500`: Internal server error

Error responses include:
```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-15T10:35:00"
}
```
