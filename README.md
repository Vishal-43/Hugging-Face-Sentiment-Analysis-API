# Sentiment Analysis REST API

A comprehensive Flask-based REST API for sentiment analysis using Hugging Face transformer models. Supports multiple languages, batch processing, historical data tracking, and more.

## Features

### Core Features ✅
- **Model Setup**
  - Hugging Face transformer models (DistilBERT for English, BERT multilingual for other languages)
  - Automatic model caching for improved performance
  - Confidence scores for all predictions
  - Multiple language support (English, Spanish, French, German, Multilingual)

- **API Endpoints**
  - `/api/analyze` - Single text sentiment analysis
  - `/api/batch` - Batch processing (up to 100 texts)
  - `/api/history` - Historical results with filtering and pagination
  - `/health` - Health check endpoint

- **Data Processing**
  - Intelligent text preprocessing
  - Emoji handling (converts emojis to text descriptions)
  - URL removal
  - Character limit handling (512 characters max)
  - Mention and hashtag cleaning

### Bonus Features ⭐
- **API Key Authentication** - Optional authentication using X-API-Key header
- **Export Functionality** - Export historical data in JSON or CSV format
- **Statistics Dashboard** - Comprehensive analytics endpoint
- **Performance Metrics** - Processing time tracking for each request

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd assignment
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication (Optional)
Include the API key in the request header:
```
X-API-Key: demo-api-key-12345
```

Demo API keys:
- `demo-api-key-12345`
- `test-key-67890`

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "models_loaded": ["en"],
  "version": "1.0.0"
}
```

#### 2. Single Text Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "text": "I absolutely love this product! It's amazing!",
  "language": "en",
  "save_history": true
}
```

**Response:**
```json
{
  "text": "I absolutely love this product! It's amazing!",
  "processed_text": "I absolutely love this product! It's amazing!",
  "sentiment": "POSITIVE",
  "confidence": 0.9998,
  "language": "en",
  "processing_time_seconds": 0.156
}
```

#### 3. Batch Processing
```http
POST /api/batch
Content-Type: application/json

{
  "texts": [
    "This is fantastic!",
    "I'm very disappointed",
    "It's okay, nothing special"
  ],
  "language": "en",
  "save_history": true
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "This is fantastic!",
      "processed_text": "This is fantastic!",
      "sentiment": "POSITIVE",
      "confidence": 0.9995,
      "language": "en",
      "processing_time_seconds": 0.145
    },
    {
      "text": "I'm very disappointed",
      "processed_text": "I'm very disappointed",
      "sentiment": "NEGATIVE",
      "confidence": 0.9987,
      "language": "en",
      "processing_time_seconds": 0.142
    },
    {
      "text": "It's okay, nothing special",
      "processed_text": "It's okay, nothing special",
      "sentiment": "NEUTRAL",
      "confidence": 0.7234,
      "language": "en",
      "processing_time_seconds": 0.148
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

#### 4. Historical Results
```http
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

#### 5. Statistics
```http
GET /api/stats
```

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

#### 6. Export Data
```http
GET /api/export?format=json
GET /api/export?format=csv
```

**Response:** Downloads historical data in the specified format.

## Supported Languages

- `en` - English (DistilBERT model)
- `multilingual` - Multiple languages (BERT multilingual)
- `es` - Spanish
- `fr` - French
- `de` - German

## Text Preprocessing

The API automatically handles:
- **Emojis**: Converted to text descriptions (e.g., 😊 → "smiling face")
- **URLs**: Removed automatically
- **Mentions/Hashtags**: Symbols removed, text preserved
- **Whitespace**: Normalized and cleaned
- **Length**: Truncated to 512 characters if necessary

## Testing Examples

### Example 1: Social Media Post with Emojis
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Just got my new phone! 📱😍 Love it so much! #awesome"}'
```

### Example 2: Batch Analysis
```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Best purchase ever!",
      "Worst experience of my life",
      "It was fine, met expectations"
    ]
  }'
```

### Example 3: With API Key
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-api-key-12345" \
  -d '{"text": "Amazing product!"}'
```

### Example 4: Multilingual
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "¡Me encanta este producto!", "language": "es"}'
```

## Performance Metrics

The API tracks and returns:
- **Processing Time**: Time taken for sentiment analysis
- **Confidence Scores**: Model confidence for each prediction
- **Success Rate**: Batch processing statistics
- **Historical Trends**: 24-hour sentiment distribution

### Typical Performance
- Single text analysis: 100-200ms (after model loaded)
- Batch processing (10 texts): 1-2 seconds
- First request: 2-5 seconds (model loading time)

## Error Handling

The API provides clear error messages:

```json
{
  "error": "Missing required field: text"
}
```

Common error codes:
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (endpoint doesn't exist)
- `500` - Internal Server Error

## Database

The application uses SQLite to store historical results:
- Database file: `sentiment_history.db`
- Automatic schema creation on first run
- Stores: text, sentiment, confidence, language, timestamp

## Project Structure

```
assignment/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── API_DOCUMENTATION.md        # Detailed API docs
├── POSTMAN_COLLECTION.json     # Postman collection for testing
├── test_suite.py              # Automated test suite
├── sentiment_history.db       # SQLite database (created on first run)
└── .gitignore                 # Git ignore file
```

## Development

### Running in Development Mode
```bash
python app.py
```

### Running in Production
```bash
# Use gunicorn or similar WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Configuration

Environment variables:
- `SECRET_KEY` - Flask secret key (default: dev-secret-key-change-in-production)
- `PORT` - Server port (default: 5000)

## Limitations

- Maximum request size: 16MB
- Maximum batch size: 100 texts
- Maximum text length: 512 characters (truncated automatically)
- Model runs on CPU by default (change `device=-1` to `device=0` for GPU)

## Future Enhancements

Potential improvements:
- Real-time Twitter/social media integration
- Interactive sentiment trends dashboard
- Support for more languages
- Custom model fine-tuning
- WebSocket support for real-time analysis
- Rate limiting
- User authentication and quotas

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open-source and available under the MIT License.

## Support

For issues or questions:
- Check the API documentation
- Review the test suite examples
- Open an issue on GitHub

## Acknowledgments

- Hugging Face for transformer models
- Flask framework
- Open-source community
#   H u g g i n g - F a c e - S e n t i m e n t - A n a l y s i s - A P I  
 #   H u g g i n g - F a c e - S e n t i m e n t - A n a l y s i s - A P I  
 #   H u g g i n g - F a c e - S e n t i m e n t - A n a l y s i s - A P I  
 