#!/usr/bin/env python
"""
Simple test script to verify the API endpoints work correctly
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trendtracker.settings')
sys.path.append(os.path.dirname(__file__))

django.setup()

# Now import Django modules
import json
from django.test import RequestFactory
from tracker.views import crypto_news

# Test the API
factory = RequestFactory()

def test_crypto_news_api():
    print("Testing crypto news API...")
    
    # Test GET request
    request = factory.get('/crypto_news/', {'coin': 'bitcoin'})
    response = crypto_news(request)
    
    print(f"Status Code: {response.status_code}")
    
    try:
        data = json.loads(response.content.decode())
        print(f"Response keys: {list(data.keys())}")
        
        if 'error' in data:
            print(f"API returned error: {data['error']}")
            if 'message' in data:
                print(f"Error message: {data['message']}")
        else:
            print("API response looks good!")
            print(f"Content preview: {data.get('content', 'No content')[:100]}...")
            print(f"Sentiment: {data.get('sentiment', 'No sentiment')}")
            
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Raw content: {response.content.decode()}")

if __name__ == "__main__":
    test_crypto_news_api()
