from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from mistralai import Mistral
import requests
import json
import logging
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

JINA_API_KEY = os.getenv("API_KEY") 
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def index(request):
    logger.info("Index page requested")
    return render(request, 'tracker/index.html')

@csrf_exempt
def crypto_news(request):
    logger.info("Crypto news endpoint called")
    try:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                coin_name = data.get('coin', 'bitcoin')
                logger.info(f"POST request parsed with coin: {coin_name}")
            except json.JSONDecodeError:
                coin_name = request.POST.get('coin', 'bitcoin')
                logger.warning(f"JSON decode failed, using form data. Coin: {coin_name}")
        else:
            coin_name = request.GET.get('coin', 'bitcoin')
            logger.info(f"GET request with coin: {coin_name}")

        response_data = get_combined_news_and_sentiment(coin_name)
        logger.info(f"Response data generated successfully")
        
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error in crypto_news view: {str(e)}")
        return JsonResponse({
            "error": "Internal server error",
            "message": str(e)
        }, status=500)

def get_combined_news_and_sentiment(coin_name):
    logger.info(f"Fetching news and sentiment for {coin_name}")
    
    # Validate API keys
    if not JINA_API_KEY or not MISTRAL_API_KEY:
        logger.error("Missing API keys")
        return {
            "error": "API configuration error",
            "content": "Unable to fetch news data due to missing API keys.",
            "urls": [],
            "sentiment": "Neutral"
        }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }

    prompt = f"Provide the latest news and current market sentiment for {coin_name}."
    logger.info(f"Using prompt: {prompt}")

    data = {
        "model": "jina-deepsearch-v1",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "reasoning_effort": "low",
        "max_attempts": 1,
        "no_direct_answer": False,
        "only_hostnames": [
            "https://cointelegraph.com",
            "https://u.today",
            "https://coindesk.com",
            "https://coincodex.com",
            "https://coingape.com",
            "https://ambcrypto.com",
            "https://crypto.news",
            "https://bitcoinist.com",
            "https://dailyhodl.com",
            "https://beincrypto.com"
        ],
    }

    try:
        logger.info("Making request to Jina API")
        response = requests.post('https://deepsearch.jina.ai/v1/chat/completions', 
            headers=headers, 
            json=data, 
            timeout=180
        )

        logger.info(f"Jina API response status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Jina API Response received successfully")
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                full_content = response_data['choices'][0]['message']['content']
                content = get_summary(full_content)
                urls_list = response_data.get('visitedURLs', [])
                sentiment = extract_sentiment(full_content)

                result = {
                    "content": content,
                    "urls": urls_list,
                    "sentiment": sentiment
                }

                logger.info("Processed result successfully")
                return result
            else:
                logger.error("Invalid response structure from Jina API")
                return {
                    "error": "Invalid API response",
                    "content": "No content available",
                    "urls": [],
                    "sentiment": "Neutral"
                }

        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            return {
                "error": f"API request failed with status {response.status_code}",
                "content": "Unable to fetch news data at this time.",
                "urls": [],
                "sentiment": "Neutral"
            }

    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return {
            "error": "Request timeout",
            "content": "Request timed out. Please try again.",
            "urls": [],
            "sentiment": "Neutral"
        }
    except Exception as e:
        logger.error(f"Error in get_combined_news_and_sentiment: {str(e)}")
        return {
            "error": str(e),
            "content": "An error occurred while fetching news data.",
            "urls": [],
            "sentiment": "Neutral"
        }

def get_summary(content):
    logger.info("Generating summary")
    try:
        if not MISTRAL_API_KEY:
            logger.error("Missing Mistral API key")
            return "Summary unavailable due to API configuration error."
            
        client = Mistral(api_key=MISTRAL_API_KEY)

        messages = [
            {
                "role": "system",
                "content": "Summarize the following text in 200 words."
            },
            {
                "role": "user",
                "content": content
            }
        ]

        logger.info("Making request to Mistral API")
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,        
        )

        bot_reply = chat_response.choices[0].message.content
        logger.info("Mistral API response received successfully")
        return bot_reply
        
    except Exception as e:
        logger.error(f"Error in get_summary: {str(e)}")
        return f"Summary generation failed: {str(e)}"

def extract_sentiment(content):
    logger.info("Extracting sentiment")
    try:
        if not MISTRAL_API_KEY:
            logger.error("Missing Mistral API key")
            return "Neutral"
            
        client = Mistral(api_key=MISTRAL_API_KEY)

        messages = [
            {
                "role": "system",
                "content": "Extract the sentiment of the following text. The sentiment can be bullish, bearish or neutral. Reply in one word"
            },
            {
                "role": "user",
                "content": content
            }
        ]

        logger.info("Making request to Mistral API")
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,        
        )

        bot_reply = chat_response.choices[0].message.content.lower()
        logger.info("Mistral API response received successfully")

        if "bullish" in bot_reply:
            sentiment = "Bullish"
        elif "bearish" in bot_reply:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"
        
        logger.info(f"Final sentiment: {sentiment}")
        return sentiment
        
    except Exception as e:
        logger.error(f"Error in extract_sentiment: {str(e)}")
        return "Neutral"
