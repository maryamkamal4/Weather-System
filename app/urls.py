from django.urls import path
from app.views import WeatherView

urlpatterns = [
    path('', WeatherView.as_view(), name='index'),
]