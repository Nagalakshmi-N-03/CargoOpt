# CargoOpt API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#request-response-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Code Examples](#code-examples)
8. [Webhooks](#webhooks)

---

## Introduction

### Base URL

```
Production: https://api.cargoopt.com/api
Development: http://localhost:5000/api
```

### API Version

Current Version: `v1.0.0`

### Content Type

All requests and responses use JSON:
```
Content-Type: application/json
Accept: application/json
```

---

## Authentication

### API Keys

Authenticate using Bearer token:

```http
Authorization: Bearer YOUR_API_KEY
```

### Obtaining API Keys

1. Log in to CargoOpt dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Store securely (shown only once)

### Security

- Use HTTPS in production
- Never commit API keys to version control
- Rotate keys regularly
- Use environment variables

---

## API Endpoints

### Health Check

#### GET /health

Check API status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy"
  }
}
```

### API Information

#### GET /info

Get API capabilities and configuration

**Response:**
```json
{
  "api": {
    "name": "CargoOpt API",
    "version": "1.0.0",
    "environment": "production"
  },
  "capabilities": {
    "optimization_algorithms": ["genetic_algorithm", "constraint_programming"],
    "supported_item_types": ["glass", "wood", "metal", ...],
    "storage_conditions": ["standard", "refrigerated", "frozen", "hazardous"],
    "container_types": ["standard", "high_cube", "refrigerated", ...],
    "hazard_classes": ["1", "2.1", "2.2", ...]
  },
  "limits": {
    "max_file_size_mb": 10,
    "max_computation_time_seconds": 300,
    "max_items_per_request": 1000
  }
}
```

### Optimization

#### POST /optimize

Submit container packing optimization request

**Request Body:**
```json
{
  "container": {
    "container_id": "CONT001",
    "name": "20ft Standard",
    "length": 5898,
    "width": 2352,
    "height": 2393,
    "max_weight": 28180,
    "container_type": "standard"
  },
  "items": [
    {
      "item_id": "ITEM001",
      "name": "Box A",
      "length": 1000,
      "width": 800,
      "height": 600,
      "weight": 50,
      "quantity": 5,
      "fragile": false,
      "stackable": true,
      "rotation_allowed": true,
      "priority": 3
    }
  ],
  "algorithm": "genetic",
  "parameters": {
    "population_size": 100,
    "generations": 50,
    "time_limit": 300
  },
  "optimize_for": "balanced"
}
```

**Response (Synchronous):**
```json
{
  "optimization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "utilization": 78.5,
  "total_items": 5,
  "items_packed": 5,
  "items_unpacked": 0,
  "placements": [...],
  "metrics": {
    "computation_time": 45.23,
    "fitness_score": 0.8234,
    "weight_utilization": 65.3
  }
}
```

**Response (Asynchronous):**
```json
{
  "optimization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Optimization started"
}
```

#### GET /optimize/{optimization_id}

Get optimization results

**Parameters:**
- `optimization_id` (path): UUID of optimization

**Response:**
```json
{
  "optimization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "algorithm_used": "genetic",
  "utilization": 78.5,
  "fitness_score": 0.8234,
  "computation_time": 45.23,
  "placements": [
    {
      "item_id": "ITEM001",
      "item_name": "Box A",
      "position": {"x": 0, "y": 0, "z": 0},
      "dimensions": {"length": 1000, "width": 800, "height": 600},
      "rotation": 0,
      "weight": 50
    }
  ],
  "unpacked_items": [],
  "violations": [],
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:45Z"
}
```

#### GET /optimize/{optimization_id}/status

Get optimization status (for polling)

**Response:**
```json
{
  "optimization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 45.5,
  "current_generation": 23,
  "best_fitness": 0.7512,
  "estimated_time_remaining": 30
}
```

#### POST /optimize/{optimization_id}/cancel

Cancel running optimization

**Response:**
```json
{
  "optimization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Optimization cancelled successfully"
}
```

### Validation

#### POST /validate

Validate optimization request without running

**Request Body:**
```json
{
  "container": {...},
  "items": [...]
}
```

**Response:**
```json
{
  "valid": true,
  "warnings": [
    "Total item volume (45.2 m³) approaches container capacity (50.0 m³)"
  ],
  "errors": []
}
```

### Containers

#### GET /containers

List all containers

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `container_type` (string): Filter by type
- `search` (string): Search by name or ID

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "container_id": "CONT001",
      "name": "20ft Standard A1",
      "length": 5898,
      "width": 2352,
      "height": 2393,
      "max_weight": 28180,
      "container_type": "standard",
      "volume_m3": 33.2,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### GET /containers/{container_id}

Get specific container

**Response:**
```json
{
  "id": 1,
  "container_id": "CONT001",
  "name": "20ft Standard A1",
  "length": 5898,
  "width": 2352,
  "height": 2393,
  "max_weight": 28180,
  "container_type": "standard",
  "volume_m3": 33.2,
  "volume_display": "33.2 m³",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### POST /containers

Create new container

**Request Body:**
```json
{
  "container_id": "CONT002",
  "name": "Custom Container",
  "length": 6000,
  "width": 2400,
  "height": 2500,
  "max_weight": 30000,
  "container_type": "standard",
  "description": "Custom size container"
}
```

**Response:**
```json
{
  "id": 2,
  "container_id": "CONT002",
  "message": "Container created successfully"
}
```

#### PUT /containers/{container_id}

Update container

**Request Body:**
```json
{
  "name": "Updated Name",
  "max_weight": 29000
}
```

**Response:**
```json
{
  "id": 2,
  "message": "Container updated successfully"
}
```

#### DELETE /containers/{container_id}

Delete container

**Response:**
```json
{
  "message": "Container deleted successfully"
}
```

### Items

#### GET /items

List all items

**Query Parameters:**
- `page`, `per_page`, `item_type`, `search` (same as containers)

**Response:** (Similar structure to containers)

#### GET /items/{item_id}

Get specific item

#### POST /items

Create new item

**Request Body:**
```json
{
  "item_id": "ITEM002",
  "name": "Electronics Box",
  "length": 400,
  "width": 300,
  "height": 250,
  "weight": 15.5,
  "item_type": "electronics",
  "fragile": true,
  "stackable": true,
  "max_stack_weight": 50,
  "rotation_allowed": true,
  "keep_upright": false,
  "priority": 1,
  "color": "#4169E1"
}
```

#### PUT /items/{item_id}

Update item

#### DELETE /items/{item_id}

Delete item

#### POST /items/bulk

Create multiple items

**Request Body:**
```json
{
  "items": [
    {
      "item_id": "ITEM003",
      "name": "Box A",
      ...
    },
    {
      "item_id": "ITEM004",
      "name": "Box B",
      ...
    }
  ]
}
```

**Response:**
```json
{
  "success_count": 2,
  "error_count": 0,
  "created_ids": ["ITEM003", "ITEM004"],
  "errors": []
}
```

#### POST /items/import

Import items from CSV

**Request:**
```http
POST /api/items/import
Content-Type: multipart/form-data

file: items.csv
```

**Response:**
```json
{
  "imported_count": 25,
  "skipped_count": 2,
  "errors": [
    {"row": 3, "error": "Invalid weight value"},
    {"row": 7, "error": "Missing required field: length"}
  ]
}
```

### History

#### GET /history

Get optimization history

**Query Parameters:**
- `page`, `per_page`: Pagination
- `status`: Filter by status (completed, failed, running, pending)
- `algorithm`: Filter by algorithm
- `from_date`, `to_date`: Date range filter
- `sort`: Sort field (started_at, utilization, computation_time)
- `order`: Sort order (asc, desc)

**Response:**
```json
{
  "data": [
    {
      "optimization_id": "uuid",
      "status": "completed",
      "utilization": 78.5,
      "items_packed": 25,
      "total_items": 25,
      "algorithm": "genetic",
      "computation_time": 45.23,
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:45Z"
    }
  ],
  "pagination": {...}
}
```

### Exports

#### POST /exports/{optimization_id}

Export optimization results

**Query Parameters:**
- `format`: pdf, json, csv, xlsx, png, jpg

**Request Body (optional for PDF):**
```json
{
  "include_3d_view": true,
  "include_item_list": true,
  "include_statistics": true,
  "dpi": 300,
  "page_size": "A4"
}
```

**Response:**
Binary file download with appropriate Content-Type

### Statistics

#### GET /stats

Get system-wide statistics

**Response:**
```json
{
  "optimizations": {
    "total": 1542,
    "completed": 1489,
    "failed": 53,
    "average_utilization": 76.3,
    "average_computation_time": 52.7
  },
  "containers": {
    "total": 45
  },
  "items": {
    "total": 328,
    "types": 8
  },
  "recent_optimizations": [...]
}
```

### Configuration

#### GET /config

Get system configuration (public settings)

**Response:**
```json
{
  "configurations": [
    {
      "key": "ga_population_size",
      "value": 100,
      "type": "integer",
      "description": "Genetic algorithm population size"
    }
  ]
}
```

#### GET /config/{key}

Get specific configuration value

#### PUT /config/{key}

Update configuration value (admin only)

**Request Body:**
```json
{
  "value": 150
}
```

### Database Status

#### GET /db/status

Get database connection status

**Response:**
```json
{
  "status": "connected",
  "pool": {
    "status": "active",
    "min_connections": 1,
    "max_connections": 5
  },
  "tables": {
    "containers": 45,
    "items": 328,
    "optimizations": 1542,
    "placements": 38550
  }
}
```

---

## Request/Response Formats

### Common Response Structure

**Success Response:**
```json
{
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Response:**
```json
{
  "error": "Bad Request",
  "message": "Invalid container dimensions",
  "status_code": 400,
  "details": {
    "field": "length",
    "issue": "Must be greater than 0"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Data Types

**Container Object:**
```typescript
{
  container_id: string,
  name?: string,
  length: number,          // mm
  width: number,           // mm
  height: number,          // mm
  max_weight: number,      // kg
  container_type: 'standard' | 'high_cube' | 'refrigerated' | ...
}
```

**Item Object:**
```typescript
{
  item_id: string,
  name?: string,
  length: number,          // mm
  width: number,           // mm
  height: number,          // mm
  weight: number,          // kg
  quantity?: number,
  item_type?: string,
  storage_condition?: string,
  fragile?: boolean,
  stackable?: boolean,
  max_stack_weight?: number,
  rotation_allowed?: boolean,
  keep_upright?: boolean,
  hazard_class?: string,
  priority?: number,       // 1-10
  color?: string          // hex color
}
```

**Placement Object:**
```typescript
{
  item_id: string,
  item_name: string,
  position: {x: number, y: number, z: number},
  dimensions: {length: number, width: number, height: number},
  rotation: number,        // 0, 90, 180, 270
  weight: number,
  color?: string
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `204 No Content`: Successful with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "error": "Validation Error",
  "message": "Input validation failed",
  "status_code": 422,
  "field_errors": {
    "container.length": ["Must be greater than 100"],
    "items[0].weight": ["Required field"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Scenarios

**Validation Error (422):**
```json
{
  "error": "Validation Error",
  "message": "Container dimensions invalid",
  "details": {
    "field": "length",
    "provided": -100,
    "requirement": "Must be positive integer between 100 and 50000"
  }
}
```

**Not Found (404):**
```json
{
  "error": "Not Found",
  "message": "Optimization with ID 'xyz' not found"
}
```

**Rate Limit (429):**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0
}
```

---

## Rate Limiting

### Limits

**Free Tier:**
- 100 requests per hour
- 10 optimizations per day
- 1 concurrent optimization

**Pro Tier:**
- 1000 requests per hour
- 100 optimizations per day
- 3 concurrent optimizations

**Enterprise:**
- Custom limits
- Dedicated resources

### Headers

**Request:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642252800
```

**Response:**
Same headers plus:
```http
X-RateLimit-Used: 1
```

### Handling Rate Limits

```python
response = requests.get(url, headers=headers)

if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request
```

---

## Code Examples

### Python

```python
import requests
import json

API_KEY = "your_api_key_here"
BASE_URL = "https://api.cargoopt.com/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Submit optimization
optimization_data = {
    "container": {
        "length": 5898,
        "width": 2352,
        "height": 2393,
        "max_weight": 28180
    },
    "items": [
        {
            "item_id": "ITEM001",
            "length": 1000,
            "width": 800,
            "height": 600,
            "weight": 50,
            "quantity": 5
        }
    ],
    "algorithm": "genetic"
}

response = requests.post(
    f"{BASE_URL}/optimize",
    headers=headers,
    json=optimization_data
)

if response.status_code == 200:
    result = response.json()
    optimization_id = result["optimization_id"]
    print(f"Optimization started: {optimization_id}")
    
    # Poll for results
    while True:
        status_response = requests.get(
            f"{BASE_URL}/optimize/{optimization_id}/status",
            headers=headers
        )
        status = status_response.json()
        
        if status["status"] == "completed":
            # Get full results
            result_response = requests.get(
                f"{BASE_URL}/optimize/{optimization_id}",
                headers=headers
            )
            results = result_response.json()
            print(f"Utilization: {results['utilization']}%")
            break
        elif status["status"] == "failed":
            print("Optimization failed")
            break
        
        time.sleep(5)  # Wait 5 seconds before polling again
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.cargoopt.com/api';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

async function runOptimization() {
  try {
    // Submit optimization
    const response = await axios.post(
      `${BASE_URL}/optimize`,
      {
        container: {
          length: 5898,
          width: 2352,
          height: 2393,
          max_weight: 28180
        },
        items: [
          {
            item_id: 'ITEM001',
            length: 1000,
            width: 800,
            height: 600,
            weight: 50,
            quantity: 5
          }
        ],
        algorithm: 'genetic'
      },
      { headers }
    );

    const optimizationId = response.data.optimization_id;
    console.log(`Optimization started: ${optimizationId}`);

    // Poll for results
    let completed = false;
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const statusResponse = await axios.get(
        `${BASE_URL}/optimize/${optimizationId}/status`,
        { headers }
      );

      if (statusResponse.data.status === 'completed') {
        const resultResponse = await axios.get(
          `${BASE_URL}/optimize/${optimizationId}`,
          { headers }
        );
        console.log(`Utilization: ${resultResponse.data.utilization}%`);
        completed = true;
      } else if (statusResponse.data.status === 'failed') {
        console.error('Optimization failed');
        completed = true;
      }
    }
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

runOptimization();
```

### cURL

```bash
# Submit optimization
curl -X POST https://api.cargoopt.com/api/optimize \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "container": {
      "length": 5898,
      "width": 2352,
      "height": 2393,
      "max_weight": 28180
    },
    "items": [
      {
        "item_id": "ITEM001",
        "length": 1000,
        "width": 800,
        "height": 600,
        "weight": 50,
        "quantity": 5
      }
    ],
    "algorithm": "genetic"
  }'

# Get results
curl -X GET https://api.cargoopt.com/api/optimize/{optimization_id} \
  -H "Authorization: Bearer YOUR_API_KEY"

# Export PDF
curl -X POST "https://api.cargoopt.com/api/exports/{optimization_id}?format=pdf" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  --output result.pdf
```

---

## Webhooks

### Configuration

Set up webhooks in dashboard under Settings > Webhooks

### Events

**optimization.completed**
```json
{
  "event": "optimization.completed",
  "optimization_id": "uuid",
  "status": "completed",
  "utilization": 78.5,
  "timestamp": "2024-01-15T10:30:45Z"
}
```

**optimization.failed**
```json
{
  "event": "optimization.failed",
  "optimization_id": "uuid",
  "error": "Timeout exceeded",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### Webhook Verification

Verify webhook signatures:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

**CargoOpt API Documentation - Version 1.0.0**  
*Last Updated: November 2024*