from django.urls import path

from fetch.views import search

app_name = 'everbook'
urlpatterns = [
    path('search/', search, name='search'),
]
