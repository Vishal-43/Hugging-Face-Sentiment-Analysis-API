# Sentiment Analysis API - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Codes](#error-codes)
7. [Rate Limiting](#rate-limiting)
8. [Best Practices](#best-practices)

## Overview

The Sentiment Analysis API provides powerful sentiment analysis capabilities using state-of-the-art Hugging Face transformer models. It supports multiple languages, batch processing, and historical tracking.

**Base URL:** `http://localhost:5000`

**API Version:** 1.0.0

## Getting Started

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```

3. **Test the API:**
   ```bash
   curl http://localhost:5000/health
   ```

### Authentication

Authentication is optional but recommended for production use.

**Header:** `X-API-Key`

**Demo API Keys:**
- `demo-api-key-12345`
- `test-key-67890`

**Example:**
```bash
curl -H "X-API-Key: demo-api-key-12345" \
     -H "Content-Type: application/json" \
     -d '{"text": "Great product!"}' \
     http://localhost:5000/api/analyze
```

## Endpoints

### 1. Health Check

Check API status and view loaded models.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "models_loaded": ["en"],
  "version": "1.0.0"
}
```

---

### 2. Single Text Analysis

Analyze sentiment of a single text.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "text": "string (required)",
  "language": "string (optional, default: 'en')",
  "save_history": "boolean (optional, default: true)"
}
```

**Supported Languages:**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `multilingual` - Auto-detect

**Response:**
```json
{
  "text": "I love this product!",
  "processed_text": "I love this product!",
  "sentiment": "POSITIVE",
  "confidence": 0.9998,
  "language": "en",
  "processing_time_seconds": 0.156
}
```

**Sentiment Values:**
- `POSITIVE` - Positive sentiment
- `NEGATIVE` - Negative sentiment
- `NEUTRAL` - Neutral sentiment

---

### 3. Batch Processing

Process multiple texts in a single request (max 100).

**Endpoint:** `POST /api/batch`

**Request Body:**
```json
{
  "texts": ["string", "string", ...],
  "language": "string (optional, default: 'en')",
  "save_history": "boolean (optional, default: true)"
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Great product!",
      "processed_text": "Great product!",
      "sentiment": "POSITIVE",
      "confidence": 0.9995,
      "language": "en",
      "processing_time_seconds": 0.145
    }
  ],
  "statistics": {
    "total": 1,
    "successful": 1,
    "failed": 0,
    "sentiment_distribution": {
      "POSITIVE": 1,
      "NEGATIVE": 0,
      "NEUTRAL": 0
    }
  }
}
```

---

### 4. Historical Results

Retrieve past sentiment analysis results with filtering and pagination.

**Endpoint:** `GET /api/history`

**Query Parameters:**
- `limit` - Number of results (default: 100, max: 1000)
- `offset` - Pagination offset (default: 0)
- `sentiment` - Filter by sentiment (POSITIVE, NEGATIVE, NEUTRAL)

**Example:**
```
GET /api/history?limit=10&offset=0&sentiment=POSITIVE
```

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "text": "I love this!",
      "sentiment": "POSITIVE",
      "confidence": 0.9998,
      "language": "en",
      "timestamp": "2024-01-15 10:30:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### 5. Statistics

Get comprehensive analytics about sentiment analysis.

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "total_analyses": 150,
  "sentiment_distribution": {
    "POSITIVE": 75,
    "NEGATIVE": 45,
    "NEUTRAL": 30
  },
  "average_confidence": {
    "POSITIVE": 0.9567,
    "NEGATIVE": 0.9234,
    "NEUTRAL": 0.7891
  },
  "recent_24h_trend": {
    "POSITIVE": 12,
    "NEGATIVE": 5,
    "NEUTRAL": 3
  }
}
```

---

### 6. Export Data

Export historical data in JSON or CSV format.

**Endpoint:** `GET /api/export`

**Query Parameters:**
- `format` - Export format (json or csv, default: json)

**Example:**
```
GET /api/export?format=csv
```

**Response:** File download (JSON or CSV)

---

### 7. API Documentation

Get interactive API documentation.

**Endpoint:** `GET /`

**Response:** JSON with complete API documentation

## Request/Response Examples

### Example 1: Social Media Post with Emojis

**Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Just got my new phone! 📱😍 Love it so much! #awesome",
    "language": "en"
  }'
```

**Response:**
```json
{
  "text": "Just got my new phone! 📱😍 Love it so much! #awesome",
  "processed_text": "Just got my new phone! mobile phone smiling face with heart eyes Love it so much! awesome",
  "sentiment": "POSITIVE",
  "confidence": 0.9996,
  "language": "en",
  "processing_time_seconds": 0.167
}
```

### Example 2: Batch Analysis of Product Reviews

**Request:**
```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Best purchase ever! Highly recommend!",
      "Terrible quality. Very disappointed.",
      "It works fine. Nothing special."
    ],
    "language": "en"
  }'
```

**Response:**
```json
{
  "results": [
    {
      "text": "Best purchase ever! Highly recommend!",
      "sentiment": "POSITIVE",
      "confidence": 0.9997,
      "language": "en",
      "processing_time_seconds": 0.142
    },
    {
      "text": "Terrible quality. Very disappointed.",
      "sentiment": "NEGATIVE",
      "confidence": 0.9989,
      "language": "en",
      "processing_time_seconds": 0.138
    },
    {
      "text": "It works fine. Nothing special.",
      "sentiment": "NEUTRAL",
      "confidence": 0.7654,
      "language": "en",
      "processing_time_seconds": 0.145
    }
  ],
  "statistics": {
    "total": 3,
    "successful": 3,
    "failed": 0,
    "sentiment_distribution": {
      "POSITIVE": 1,
      "NEGATIVE": 1,
      "NEUTRAL": 1
    }
  }
}
```

### Example 3: Multilingual Analysis

**Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "¡Este producto es increíble! Me encanta.",
    "language": "es"
  }'
```

**Response:**
```json
{
  "text": "¡Este producto es increíble! Me encanta.",
  "processed_text": "¡Este producto es increíble! Me encanta.",
  "sentiment": "POSITIVE",
  "confidence": 0.9876,
  "language": "es",
  "processing_time_seconds": 0.234
}
```

## Error Codes

### 400 Bad Request
Missing or invalid request parameters.

**Example:**
```json
{
  "error": "Missing required field: text"
}
```

### 401 Unauthorized
Invalid or missing API key (when authentication is enforced).

**Example:**
```json
{
  "error": "Invalid API key"
}
```

### 404 Not Found
Endpoint not found.

**Example:**
```json
{
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error
Server error during processing.

**Example:**
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

Currently, there are no rate limits enforced. For production deployment, consider implementing:
- Rate limiting per API key
- Request throttling
- Concurrent request limits

## Best Practices

### 1. Text Preprocessing
The API automatically handles:
- Emoji conversion
- URL removal
- Whitespace normalization
- Character limit enforcement (512 chars)

### 2. Batch Processing
For multiple texts:
- Use `/api/batch` instead of multiple `/api/analyze` calls
- Maximum 100 texts per batch
- Better performance and statistics

### 3. Error Handling
Always check response status codes:
```python
response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
else:
    error = response.json().get('error')
```

### 4. Language Detection
- Specify language when known for better accuracy
- Use `multilingual` for mixed-language content
- English model is fastest and most accurate for English text

### 5. Performance Optimization
- First request loads the model (2-5 seconds)
- Subsequent requests are much faster (100-200ms)
- Keep the server running to maintain model cache
- Use batch processing for multiple texts

### 6. Historical Data
- Set `save_history: false` for testing/development
- Query history endpoint with pagination for large datasets
- Use filtering to analyze specific sentiment types

## Model Information

### English Model
- **Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Size:** ~250MB
- **Accuracy:** Very high for English text
- **Speed:** Fast (100-200ms per text)

### Multilingual Model
- **Model:** `nlptown/bert-base-multilingual-uncased-sentiment`
- **Size:** ~700MB
- **Supported Languages:** 100+ languages
- **Accuracy:** Good for multiple languages
- **Speed:** Moderate (200-400ms per text)

## Support

For issues or questions:
1. Check this documentation
2. Review the test suite examples
3. Inspect the Postman collection
4. Contact support

## Changelog

### Version 1.0.0
- Initial release
- Core sentiment analysis features
- Multi-language support
- Batch processing
- Historical tracking
- Export functionality
- API key authentication
