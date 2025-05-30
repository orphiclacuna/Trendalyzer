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

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing form handler');
    const form = document.getElementById('cryptoForm');
    if (!form) {
        console.error('Could not find form element');
        return;
    }
    
    console.log('Form found:', form);
    
    form.addEventListener('submit', async function(e) {
        console.log('Form submitted!');
    e.preventDefault();
    
    const coinInput = document.getElementById('coinInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    
    // Reset and show loading
    error.classList.add('d-none');
    results.classList.add('d-none');
    loading.classList.remove('d-none');      try {
        const csrftoken = getCookie('csrftoken');
        console.log('CSRF token:', csrftoken);
        console.log('Making request to /api/crypto-news/ with coin:', coinInput.value.trim());
        
        const requestData = {
            coin: coinInput.value.trim()
        };
        console.log('Request data:', requestData);
        
        const response = await fetch('/api/crypto-news/', {            method: 'POST',
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
          // Convert the content to markdown and update
        const markdownContent = formatContentToMarkdown(data.content);
        document.getElementById('newsContent').innerHTML = marked.parse(markdownContent);
        
        // Update URLs list with cards
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
                urlText.textContent = urlObj.hostname + urlObj.pathname;
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
    // Split content into paragraphs
    const paragraphs = content.split('\n\n');
    
    // Format each paragraph
    return paragraphs.map(para => {
        // If paragraph starts with a number followed by a dot, make it a heading
        if (/^\d+\./.test(para)) {
            return '## ' + para;
        }
        // Add bullet points for lists
        if (para.startsWith('- ')) {
            return para;
        }
        // Wrap numbers in backticks
        para = para.replace(/(\$[\d,.]+|\d+%|[\d,.]+)/g, '`$1`');
        // Highlight important terms
        para = para.replace(/(bullish|bearish|neutral|positive|negative)/gi, '**$1**');
        return para;
    }).join('\n\n');
}
});
