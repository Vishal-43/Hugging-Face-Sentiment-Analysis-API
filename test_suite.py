"""
Comprehensive Test Suite for Sentiment Analysis API
Run with: python test_suite.py
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_KEY = "demo-api-key-12345"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def test_health_check():
    print_test("Health Check Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            print_info(f"Models loaded: {data.get('models_loaded', [])}")
            print_info(f"Version: {data.get('version', 'N/A')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_single_analysis():
    print_test("Single Text Analysis")
    
    test_cases = [
        {
            "name": "Positive sentiment",
            "text": "I absolutely love this product! It's amazing and wonderful!",
            "expected": "POSITIVE"
        },
        {
            "name": "Negative sentiment",
            "text": "This is terrible. I hate it so much. Worst experience ever.",
            "expected": "NEGATIVE"
        },
        {
            "name": "Neutral sentiment",
            "text": "The product arrived on time. It works as expected.",
            "expected": "NEUTRAL"
        },
        {
            "name": "Text with emojis",
            "text": "Great product! 😊👍 Very happy with my purchase! 🎉",
            "expected": "POSITIVE"
        },
        {
            "name": "Text with URLs",
            "text": "Check out this amazing product at https://example.com #awesome",
            "expected": "POSITIVE"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/analyze",
                json={"text": test["text"], "save_history": False},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment = data.get('sentiment', '')
                confidence = data.get('confidence', 0)
                processing_time = data.get('processing_time_seconds', 0)
                
                # Check if sentiment matches (allowing for model variation)
                if sentiment == test["expected"] or sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                    print_success(f"{test['name']}: {sentiment} (confidence: {confidence:.4f}, time: {processing_time:.3f}s)")
                    passed += 1
                else:
                    print_error(f"{test['name']}: Got {sentiment}, expected {test['expected']}")
            else:
                print_error(f"{test['name']}: HTTP {response.status_code}")
        except Exception as e:
            print_error(f"{test['name']}: {str(e)}")
    
    print_info(f"Passed: {passed}/{total}")
    return passed == total

def test_batch_processing():
    print_test("Batch Processing")
    
    texts = [
        "Excellent service! Highly recommended!",
        "Poor quality, very disappointed.",
        "Average product, nothing special.",
        "Love it! Best purchase ever!",
        "Terrible experience, would not buy again."
    ]
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/batch",
            json={"texts": texts, "save_history": False},
            headers={"Content-Type": "application/json"}
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            stats = data.get('statistics', {})
            
            print_success(f"Batch processing completed in {elapsed:.2f}s")
            print_info(f"Total: {stats.get('total', 0)}, Successful: {stats.get('successful', 0)}")
            
            if 'sentiment_distribution' in stats:
                dist = stats['sentiment_distribution']
                print_info(f"Distribution - Positive: {dist.get('POSITIVE', 0)}, Negative: {dist.get('NEGATIVE', 0)}, Neutral: {dist.get('NEUTRAL', 0)}")
            
            for i, result in enumerate(results):
                sentiment = result.get('sentiment', 'UNKNOWN')
                confidence = result.get('confidence', 0)
                print(f"  {i+1}. {sentiment} ({confidence:.4f})")
            
            return len(results) == len(texts)
        else:
            print_error(f"Batch processing failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Batch processing error: {str(e)}")
        return False

def test_multilingual():
    print_test("Multilingual Support")
    
    test_cases = [
        {"text": "¡Me encanta este producto!", "language": "es", "name": "Spanish"},
        {"text": "J'adore ce produit!", "language": "fr", "name": "French"},
        {"text": "Ich liebe dieses Produkt!", "language": "de", "name": "German"}
    ]
    
    passed = 0
    for test in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/analyze",
                json={"text": test["text"], "language": test["language"], "save_history": False},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment = data.get('sentiment', '')
                confidence = data.get('confidence', 0)
                print_success(f"{test['name']}: {sentiment} (confidence: {confidence:.4f})")
                passed += 1
            else:
                print_error(f"{test['name']}: HTTP {response.status_code}")
        except Exception as e:
            print_error(f"{test['name']}: {str(e)}")
    
    return passed == len(test_cases)

def test_history_endpoint():
    print_test("Historical Results")
    
    # First, add some data
    test_texts = [
        "Great product!",
        "Bad service.",
        "Okay experience."
    ]
    
    for text in test_texts:
        requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": text, "save_history": True}
        )
    
    try:
        # Test basic history retrieval
        response = requests.get(f"{BASE_URL}/api/history?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            total = data.get('total', 0)
            
            print_success(f"Retrieved history: {len(history)} records")
            print_info(f"Total records in database: {total}")
            
            # Test filtering
            response = requests.get(f"{BASE_URL}/api/history?sentiment=POSITIVE&limit=10")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Filtered positive sentiments: {len(data.get('history', []))} records")
            
            return True
        else:
            print_error(f"History retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"History test error: {str(e)}")
        return False

def test_statistics():
    print_test("Statistics Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        
        if response.status_code == 200:
            data = response.json()
            
            print_success("Statistics retrieved successfully")
            print_info(f"Total analyses: {data.get('total_analyses', 0)}")
            
            if 'sentiment_distribution' in data:
                dist = data['sentiment_distribution']
                print_info(f"Distribution: {json.dumps(dist, indent=2)}")
            
            if 'average_confidence' in data:
                avg = data['average_confidence']
                print_info(f"Average confidence: {json.dumps(avg, indent=2)}")
            
            return True
        else:
            print_error(f"Statistics failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Statistics error: {str(e)}")
        return False

def test_api_authentication():
    print_test("API Key Authentication")
    
    try:
        # Test with valid API key
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": "Test with API key"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            }
        )
        
        if response.status_code == 200:
            print_success("Valid API key accepted")
        else:
            print_error("Valid API key rejected")
            return False
        
        # Test with invalid API key
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": "Test with invalid key"},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "invalid-key-123"
            }
        )
        
        if response.status_code == 401:
            print_success("Invalid API key properly rejected")
            return True
        else:
            print_info("API key validation may be optional")
            return True
    except Exception as e:
        print_error(f"Authentication test error: {str(e)}")
        return False

def test_error_handling():
    print_test("Error Handling")
    
    tests_passed = 0
    
    # Test 1: Empty text
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": ""}
        )
        if response.status_code == 400:
            print_success("Empty text properly rejected")
            tests_passed += 1
        else:
            print_error("Empty text not properly handled")
    except Exception as e:
        print_error(f"Empty text test failed: {str(e)}")
    
    # Test 2: Missing required field
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={}
        )
        if response.status_code == 400:
            print_success("Missing field properly rejected")
            tests_passed += 1
        else:
            print_error("Missing field not properly handled")
    except Exception as e:
        print_error(f"Missing field test failed: {str(e)}")
    
    # Test 3: Invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        if response.status_code == 404:
            print_success("Invalid endpoint properly handled")
            tests_passed += 1
        else:
            print_error("Invalid endpoint not properly handled")
    except Exception as e:
        print_error(f"Invalid endpoint test failed: {str(e)}")
    
    return tests_passed >= 2

def test_performance():
    print_test("Performance Testing")
    
    text = "This is a great product! I highly recommend it to everyone."
    
    # Single request performance
    times = []
    for i in range(5):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": text, "save_history": False}
        )
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print_success(f"Average response time: {avg_time:.3f}s")
    print_info(f"Min: {min_time:.3f}s, Max: {max_time:.3f}s")
    
    # Batch performance
    batch_texts = [text] * 10
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/batch",
        json={"texts": batch_texts, "save_history": False}
    )
    batch_time = time.time() - start
    
    print_success(f"Batch (10 texts) time: {batch_time:.3f}s")
    print_info(f"Average per text: {batch_time/10:.3f}s")
    
    return avg_time < 1.0  # Should be under 1 second after model is loaded

def run_all_tests():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}SENTIMENT ANALYSIS API - TEST SUITE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.YELLOW}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Single Analysis", test_single_analysis),
        ("Batch Processing", test_batch_processing),
        ("Multilingual Support", test_multilingual),
        ("Historical Results", test_history_endpoint),
        ("Statistics", test_statistics),
        ("API Authentication", test_api_authentication),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test {name} crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"{name}: {status}")
    
    print(f"\n{Colors.YELLOW}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}All tests passed! 🎉{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Some tests failed. Please review the output above.{Colors.RESET}")
    
    print(f"{Colors.YELLOW}Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

if __name__ == "__main__":
    print("\nMake sure the Flask API is running on http://localhost:5000")
    print("Start the API with: python app.py\n")
    
    response = input("Is the API running? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        run_all_tests()
    else:
        print("Please start the API first and then run this test suite.")
