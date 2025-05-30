from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='index'),  # Root path for the tracker app
    path('api/crypto-news/', csrf_exempt(views.crypto_news), name='crypto_news'),  # Single endpoint for all requests
]
