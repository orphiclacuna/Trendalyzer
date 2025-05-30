from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from mistralai import Mistral
import requests
import json
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

JINA_API_KEY = os.getenv("API_KEY") 
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

print(JINA_API_KEY)

load_dotenv()

def index(request):
    logger.info("Index page requested")
    return render(request, 'tracker/index.html')

@csrf_exempt
def crypto_news(request):
    logger.info("Crypto news endpoint called")
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
    logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
    
    return JsonResponse(response_data)

def get_combined_news_and_sentiment(coin_name):
    logger.info(f"Fetching news and sentiment for {coin_name}")
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

        logger.info(f"Jina API response status: {response.status_code} -- {response}")
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Jina API Response: {json.dumps(response_data, indent=2)}")
            
            full_content = response_data['choices'][0]['message']['content']
            content = get_summary(full_content)
            urls_list = response_data['visitedURLs'][:10]
            sentiment = extract_sentiment(full_content)

            result = {
                "content": content,
                "urls": urls_list,
                "sentiment": sentiment
            }

            logger.info(f"Processed result: {json.dumps(result, indent=2)}")
            return result

        logger.error(f"API request failed with status code: {response.status_code}")
        return {"error": "Failed to fetch data"}

    except Exception as e:
        logger.error(f"Error in get_combined_news_and_sentiment: {str(e)}")
        return {"error": str(e)}

def get_summary(content):
    logger.info("Generating summary")
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
    logger.info(f"Mistral API response: {bot_reply}")
    return bot_reply

def extract_sentiment(content):
    logger.info("Extracting sentiment")
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
    logger.info(f"Mistral API response: {bot_reply}")

    if "bullish" in bot_reply:
        sentiment = "Bullish"
    elif "bearish" in bot_reply:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"
    
    logger.info(f"Final sentiment: {sentiment}")
    return sentiment
