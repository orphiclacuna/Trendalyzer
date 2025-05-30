# Trendalyzer

Trendalyzer is a Django-based web application for analyzing and visualizing cryptocurrency market sentiment. It fetches the latest news, summarizes content using AI, and displays sentiment analysis results in a user-friendly dashboard.

## Features

- Search for any cryptocurrency to get the latest news and sentiment analysis.
- AI-powered summarization of news content (using Mistral API).
- Visual sentiment indicator (bullish, bearish, neutral).
- List of news sources with favicons and direct links.
- Responsive UI built with Bootstrap and custom styles.
- Markdown rendering for formatted news summaries.

## Project Structure

```
db.sqlite3
manage.py
web_server.bat
.vscode/
tracker/
    __init__.py
    .env
    admin.py
    apps.py
    models.py
    tests.py
    urls.py
    views.py
    migrations/
    static/
        tracker/
            script.js
            style.css
    templates/
        tracker/
            index.html
trendtracker/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
```

## Setup

1. **Clone the repository** and navigate to the project directory.

2. **Install dependencies**:  
   Make sure you have Django installed. If not, install it using:
    ```sh
    pip install django
    ```

3. **Set up environment variables**:  
   Create a `.env` file in the `tracker/` directory with your API keys:
    ```
    API_KEY="your_jina_api_key"
    MISTRAL_API_KEY="your_mistral_api_key"
    ```

4. **Apply migrations**:
    ```sh
    python manage.py migrate
    ```

5. **Run the development server**:
    ```sh
    python manage.py runserver
    ```

6. **Access the app**:  
   Open [http://localhost:8000/](http://localhost:8000/) in your browser.

## Usage

- Enter a cryptocurrency name in the search bar.
- View the summarized news, sentiment badge, and source links.
- Click on any source to read the full article.

## File Highlights

- **Backend logic**: [`tracker/views.py`](tracker/views.py)
- **Frontend scripts**: [`tracker/static/tracker/script.js`](tracker/static/tracker/script.js)
- **Main template**: [`tracker/templates/tracker/index.html`](tracker/templates/tracker/index.html)
- **Custom styles**: [`tracker/static/tracker/style.css`](tracker/static/tracker/style.css)

## License

This project is for educational purposes.

---

*Powered by Django, Bootstrap, and Mistral AI.*