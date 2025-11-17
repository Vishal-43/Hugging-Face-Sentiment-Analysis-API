"""
Flask REST API for Sentiment Analysis using Hugging Face Models
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re
import emoji
from datetime import datetime
import sqlite3
import os
from functools import wraps
import time

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
API_KEYS = {'demo-api-key-12345', 'test-key-67890'}  # In production, use environment variables

# Global model cache
models_cache = {}

# Database setup
def init_db():
    """Initialize SQLite database for historical results"""
    conn = sqlite3.connect('sentiment_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sentiment_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT NOT NULL,
                  sentiment TEXT NOT NULL,
                  score REAL NOT NULL,
                  language TEXT DEFAULT 'en',
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def require_api_key(f):
    """Decorator for API key authentication (optional bonus feature)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Make API key optional - check if header exists
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key not in API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def load_model(language='en'):
    """Load and cache sentiment analysis model"""
    if language in models_cache:
        return models_cache[language]
    
    # Model selection based on language
    model_map = {
        'en': 'distilbert-base-uncased-finetuned-sst-2-english',
        'multilingual': 'nlptown/bert-base-multilingual-uncased-sentiment',
        'es': 'nlptown/bert-base-multilingual-uncased-sentiment',
        'fr': 'nlptown/bert-base-multilingual-uncased-sentiment',
        'de': 'nlptown/bert-base-multilingual-uncased-sentiment'
    }
    
    model_name = model_map.get(language, model_map['multilingual'])
    
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=-1  # Use CPU, set to 0 for GPU
        )
        models_cache[language] = sentiment_pipeline
        return sentiment_pipeline
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def preprocess_text(text):
    """Preprocess text: handle emojis, remove URLs, clean text"""
    if not text:
        return ""
    
    # Convert emojis to text descriptions
    text = emoji.demojize(text, delimiters=(" ", " "))
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove mentions and hashtags symbols but keep the text
    text = re.sub(r'[@#]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def truncate_text(text, max_length=512):
    """Truncate text to character limit"""
    return text[:max_length] if len(text) > max_length else text

def analyze_sentiment(text, language='en'):
    """Analyze sentiment of a single text"""
    start_time = time.time()
    
    # Preprocess
    processed_text = preprocess_text(text)
    processed_text = truncate_text(processed_text)
    
    if not processed_text:
        return {
            'text': text,
            'sentiment': 'NEUTRAL',
            'confidence': 0.0,
            'error': 'Empty text after preprocessing'
        }
    
    # Load model
    model = load_model(language)
    if not model:
        return {
            'text': text,
            'error': 'Model loading failed'
        }
    
    try:
        # Perform analysis
        result = model(processed_text)[0]
        
        # Normalize sentiment labels
        sentiment = result['label'].upper()
        if 'STAR' in sentiment:  # Handle multilingual model output (1-5 stars)
            stars = int(sentiment.split()[0])
            if stars <= 2:
                sentiment = 'NEGATIVE'
            elif stars == 3:
                sentiment = 'NEUTRAL'
            else:
                sentiment = 'POSITIVE'
        
        confidence = round(result['score'], 4)
        processing_time = round(time.time() - start_time, 3)
        
        return {
            'text': text,
            'processed_text': processed_text,
            'sentiment': sentiment,
            'confidence': confidence,
            'language': language,
            'processing_time_seconds': processing_time
        }
    except Exception as e:
        return {
            'text': text,
            'error': str(e)
        }

def save_to_history(text, sentiment, score, language='en'):
    """Save sentiment result to database"""
    try:
        conn = sqlite3.connect('sentiment_history.db')
        c = conn.cursor()
        c.execute('INSERT INTO sentiment_results (text, sentiment, score, language) VALUES (?, ?, ?, ?)',
                  (text, sentiment, score, language))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to history: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': list(models_cache.keys()),
        'version': '1.0.0'
    }), 200

@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze():
    """Single text sentiment analysis endpoint"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400
    
    text = data.get('text', '')
    language = data.get('language', 'en')
    save_history = data.get('save_history', True)
    
    if not text:
        return jsonify({'error': 'Text cannot be empty'}), 400
    
    result = analyze_sentiment(text, language)
    
    if 'error' not in result and save_history:
        save_to_history(text, result['sentiment'], result['confidence'], language)
    
    return jsonify(result), 200

@app.route('/api/batch', methods=['POST'])
@require_api_key
def batch_analyze():
    """Batch processing endpoint"""
    data = request.get_json()
    
    if not data or 'texts' not in data:
        return jsonify({'error': 'Missing required field: texts'}), 400
    
    texts = data.get('texts', [])
    language = data.get('language', 'en')
    save_history = data.get('save_history', True)
    
    if not isinstance(texts, list):
        return jsonify({'error': 'texts must be a list'}), 400
    
    if len(texts) > 100:
        return jsonify({'error': 'Maximum 100 texts per batch'}), 400
    
    results = []
    for text in texts:
        result = analyze_sentiment(text, language)
        results.append(result)
        
        if 'error' not in result and save_history:
            save_to_history(text, result['sentiment'], result['confidence'], language)
    
    # Calculate batch statistics
    successful = [r for r in results if 'error' not in r]
    stats = {
        'total': len(texts),
        'successful': len(successful),
        'failed': len(texts) - len(successful)
    }
    
    if successful:
        sentiments = [r['sentiment'] for r in successful]
        stats['sentiment_distribution'] = {
            'POSITIVE': sentiments.count('POSITIVE'),
            'NEGATIVE': sentiments.count('NEGATIVE'),
            'NEUTRAL': sentiments.count('NEUTRAL')
        }
    
    return jsonify({
        'results': results,
        'statistics': stats
    }), 200

@app.route('/api/history', methods=['GET'])
@require_api_key
def get_history():
    """Get historical sentiment analysis results"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    sentiment_filter = request.args.get('sentiment', None)
    
    try:
        conn = sqlite3.connect('sentiment_history.db')
        c = conn.cursor()
        
        if sentiment_filter:
            c.execute('''SELECT * FROM sentiment_results 
                        WHERE sentiment = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?''', 
                     (sentiment_filter.upper(), limit, offset))
        else:
            c.execute('''SELECT * FROM sentiment_results 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?''', 
                     (limit, offset))
        
        results = c.fetchall()
        
        # Get total count
        if sentiment_filter:
            c.execute('SELECT COUNT(*) FROM sentiment_results WHERE sentiment = ?', 
                     (sentiment_filter.upper(),))
        else:
            c.execute('SELECT COUNT(*) FROM sentiment_results')
        
        total = c.fetchone()[0]
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'text': row[1],
                'sentiment': row[2],
                'confidence': row[3],
                'language': row[4],
                'timestamp': row[5]
            })
        
        return jsonify({
            'history': history,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@require_api_key
def get_statistics():
    """Get sentiment analysis statistics"""
    try:
        conn = sqlite3.connect('sentiment_history.db')
        c = conn.cursor()
        
        # Overall statistics
        c.execute('SELECT COUNT(*) FROM sentiment_results')
        total_analyses = c.fetchone()[0]
        
        # Sentiment distribution
        c.execute('''SELECT sentiment, COUNT(*) as count 
                    FROM sentiment_results 
                    GROUP BY sentiment''')
        sentiment_dist = {row[0]: row[1] for row in c.fetchall()}
        
        # Average confidence by sentiment
        c.execute('''SELECT sentiment, AVG(score) as avg_confidence 
                    FROM sentiment_results 
                    GROUP BY sentiment''')
        avg_confidence = {row[0]: round(row[1], 4) for row in c.fetchall()}
        
        # Recent trend (last 24 hours)
        c.execute('''SELECT sentiment, COUNT(*) as count 
                    FROM sentiment_results 
                    WHERE timestamp >= datetime('now', '-1 day')
                    GROUP BY sentiment''')
        recent_trend = {row[0]: row[1] for row in c.fetchall()}
        
        conn.close()
        
        return jsonify({
            'total_analyses': total_analyses,
            'sentiment_distribution': sentiment_dist,
            'average_confidence': avg_confidence,
            'recent_24h_trend': recent_trend
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
@require_api_key
def export_history():
    """Export historical data (bonus feature)"""
    format_type = request.args.get('format', 'json')
    
    try:
        conn = sqlite3.connect('sentiment_history.db')
        c = conn.cursor()
        c.execute('SELECT * FROM sentiment_results ORDER BY timestamp DESC')
        results = c.fetchall()
        conn.close()
        
        data = []
        for row in results:
            data.append({
                'id': row[0],
                'text': row[1],
                'sentiment': row[2],
                'confidence': row[3],
                'language': row[4],
                'timestamp': row[5]
            })
        
        if format_type == 'csv':
            # Simple CSV export
            import io
            output = io.StringIO()
            output.write('id,text,sentiment,confidence,language,timestamp\n')
            for item in data:
                output.write(f"{item['id']},\"{item['text']}\",{item['sentiment']},{item['confidence']},{item['language']},{item['timestamp']}\n")
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=sentiment_history.csv'}
            )
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    docs = {
        'name': 'Sentiment Analysis API',
        'version': '1.0.0',
        'description': 'REST API for sentiment analysis using Hugging Face models',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint',
                'authentication': 'Optional'
            },
            '/api/analyze': {
                'method': 'POST',
                'description': 'Analyze sentiment of a single text',
                'authentication': 'Optional (X-API-Key header)',
                'request_body': {
                    'text': 'string (required)',
                    'language': 'string (optional, default: en)',
                    'save_history': 'boolean (optional, default: true)'
                },
                'example': {
                    'text': 'I love this product!',
                    'language': 'en'
                }
            },
            '/api/batch': {
                'method': 'POST',
                'description': 'Batch process multiple texts (max 100)',
                'authentication': 'Optional (X-API-Key header)',
                'request_body': {
                    'texts': 'array of strings (required)',
                    'language': 'string (optional, default: en)',
                    'save_history': 'boolean (optional, default: true)'
                },
                'example': {
                    'texts': ['Great product!', 'Terrible service', 'It was okay']
                }
            },
            '/api/history': {
                'method': 'GET',
                'description': 'Get historical sentiment analysis results',
                'authentication': 'Optional (X-API-Key header)',
                'query_parameters': {
                    'limit': 'integer (optional, default: 100)',
                    'offset': 'integer (optional, default: 0)',
                    'sentiment': 'string (optional, filter by sentiment)'
                }
            },
            '/api/stats': {
                'method': 'GET',
                'description': 'Get sentiment analysis statistics',
                'authentication': 'Optional (X-API-Key header)'
            },
            '/api/export': {
                'method': 'GET',
                'description': 'Export historical data',
                'authentication': 'Optional (X-API-Key header)',
                'query_parameters': {
                    'format': 'string (optional, json or csv, default: json)'
                }
            }
        },
        'supported_languages': ['en', 'es', 'fr', 'de', 'multilingual'],
        'authentication': {
            'type': 'API Key (Optional)',
            'header': 'X-API-Key',
            'demo_keys': ['demo-api-key-12345', 'test-key-67890']
        }
    }
    return jsonify(docs), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Pre-load English model for faster first request
    print("Loading English sentiment analysis model...")
    load_model('en')
    print("Model loaded successfully!")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
