// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Cryptocurrency list for autocomplete
const cryptocurrencies = [
    { name: "Bitcoin", symbol: "BTC" },
    { name: "Ethereum", symbol: "ETH" },
    { name: "Tether", symbol: "USDT" },
    { name: "XRP", symbol: "XRP" },
    { name: "BNB", symbol: "BNB" },
    { name: "Solana", symbol: "SOL" },
    { name: "USD Coin", symbol: "USDC" },
    { name: "Dogecoin", symbol: "DOGE" },
    { name: "Cardano", symbol: "ADA" },
    { name: "TRON", symbol: "TRX" },
    { name: "Wrapped Bitcoin", symbol: "WBTC" },
    { name: "Chainlink", symbol: "LINK" },
    { name: "Avalanche", symbol: "AVAX" },
    { name: "Stellar", symbol: "XLM" },
    { name: "Shiba Inu", symbol: "SHIB" },
    { name: "Toncoin", symbol: "TON" },
    { name: "Bitcoin Cash", symbol: "BCH" },
    { name: "Polkadot", symbol: "DOT" },
    { name: "Litecoin", symbol: "LTC" },
    { name: "Pepe", symbol: "PEPE" }
];

// Initialize autocomplete functionality
function initializeAutocomplete() {
    const coinInput = document.getElementById('coinInput');
    const autocompleteResults = document.getElementById('autocompleteResults');
    const clearIcon = document.getElementById('clearIcon');

    // Handle input changes
    coinInput.addEventListener('input', () => {
        const query = coinInput.value.toLowerCase().trim();
        
        // Show/hide clear icon
        clearIcon.style.display = coinInput.value ? 'block' : 'none';
        
        // Clear results if query is empty
        if (!query) {
            autocompleteResults.style.display = 'none';
            autocompleteResults.innerHTML = '';
            return;
        }

        // Filter cryptocurrencies
        const filtered = cryptocurrencies.filter(crypto =>
            crypto.name.toLowerCase().includes(query) || 
            crypto.symbol.toLowerCase().includes(query)
        );

        if (filtered.length > 0) {
            autocompleteResults.innerHTML = '';
            autocompleteResults.style.display = 'block';
            
            filtered.slice(0, 8).forEach(crypto => { // Limit to 8 results
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                item.textContent = `${crypto.name} (${crypto.symbol})`;
                item.addEventListener('click', () => {
                    coinInput.value = crypto.name;
                    autocompleteResults.style.display = 'none';
                    autocompleteResults.innerHTML = '';
                    clearIcon.style.display = 'block';
                });
                autocompleteResults.appendChild(item);
            });
        } else {
            autocompleteResults.style.display = 'none';
            autocompleteResults.innerHTML = '';
        }
    });

    // Clear icon functionality
    clearIcon.addEventListener('click', () => {
        coinInput.value = '';
        clearIcon.style.display = 'none';
        autocompleteResults.style.display = 'none';
        autocompleteResults.innerHTML = '';
        coinInput.focus();
    });

    // Hide autocomplete when clicking outside
    document.addEventListener('click', (e) => {
        if (!autocompleteResults.contains(e.target) && e.target !== coinInput) {
            autocompleteResults.style.display = 'none';
            autocompleteResults.innerHTML = '';
        }
    });
}

// Sentiment mapping for images (if needed in future)
const sentimentImageMap = {
    'bullish': '/static/tracker/assets/Bullish.png',
    'bearish': '/static/tracker/assets/Bearish.png', 
    'neutral': '/static/tracker/assets/Neutral.png'
};

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize autocomplete
    initializeAutocomplete();
    
    const form = document.getElementById('cryptoForm');
    if (!form) {
        console.error('Could not find form element');
        return;
    }
    
    
    form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const coinInput = document.getElementById('coinInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    
    // Reset and show loading
    error.classList.add('d-none');
    results.classList.add('d-none');
    loading.classList.remove('d-none');      
    try {
        const csrftoken = getCookie('csrftoken');
        
        const requestData = {
            coin: coinInput.value.trim()
        };
        
        const response = await fetch('/api/crypto-news/', {            
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update sentiment badge
        const sentimentBadge = document.querySelector('#sentimentIndicator .badge');
        sentimentBadge.textContent = data.sentiment;
        sentimentBadge.className = `badge badge-${data.sentiment.toLowerCase()}`;

        // Update hero image if available
        const heroImage = document.getElementById('heroImage');
        if (data.hero_image) {
            heroImage.src = data.hero_image;
            heroImage.style.display = 'block';
        } else {
            heroImage.style.display = 'none';
        }

        // Update sentiment meter if available
        const sentimentMeter = document.getElementById('sentimentMeter');
        if (sentimentImageMap[data.sentiment.toLowerCase()]) {
            sentimentMeter.src = sentimentImageMap[data.sentiment.toLowerCase()];
            sentimentMeter.style.display = 'block';
        } else {
            sentimentMeter.style.display = 'none';
        }

        const markdownContent = formatContentToMarkdown(data.content);
        document.getElementById('newsContent').innerHTML = marked.parse(markdownContent);
        

        const urlsList = document.getElementById('urlsList');
        urlsList.innerHTML = '';
        data.urls.forEach(url => {
            const card = document.createElement('a');
            card.href = url;
            card.target = '_blank';
            card.className = 'url-card';
            
            // Create favicon element
            const favicon = document.createElement('img');
            try {
                const domain = new URL(url).hostname;
                favicon.src = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
            } catch {
                favicon.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🌐</text></svg>';
            }
            favicon.width = 16;
            favicon.height = 16;
            favicon.className = 'icon';
            
            // Create URL text
            const urlText = document.createElement('span');
            urlText.className = 'url-text';
            try {
                const urlObj = new URL(url);
                urlText.textContent = urlObj.hostname;
            } catch {
                urlText.textContent = url;
            }
            
        card.appendChild(favicon);
        card.appendChild(urlText);
        urlsList.appendChild(card);
    });
    
    // Show results
    results.classList.remove('d-none');
    
} catch (err) {
        error.textContent = err.message || 'An error occurred while fetching the data';
        error.classList.remove('d-none');
    } finally {
        loading.classList.add('d-none');
    }
});

function formatContentToMarkdown(content) {
    const paragraphs = content.split('\n\n');
    
    return paragraphs.map(para => {
        if (/^\d+\./.test(para)) {
            return '## ' + para;
        }
        if (para.startsWith('- ')) {
            return para;
        }
        para = para.replace(/(\$[\d,.]+|\d+%|[\d,.]+)/g, '`$1`');
        para = para.replace(/(bullish|bearish|neutral|positive|negative)/gi, '**$1**');
        return para;
    }).join('\n\n');
}
});
