import datetime
import logging
import requests
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

class WeatherView(View):
    template_name = "index.html"
    api_key = "b99fd87a1419cc2cdd6d695ab387db7a"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        city1 = request.POST.get('city1', None)
        city2 = request.POST.get('city2', None)

        # # Read the API key from a file
        # self.api_key = self.read_api_key_from_file("API_Key.txt")

        weather_data1, daily_forecasts1 = self.fetch_weather_and_forecast(city1)
        weather_data2, daily_forecasts2 = self.fetch_weather_and_forecast(city2) if city2 else (None, None)

        context = {
            "weather_data1": weather_data1,
            "weather_data2": weather_data2,
            "daily_forecasts1": daily_forecasts1,
            "daily_forecasts2": daily_forecasts2
        }

        return render(request, self.template_name, context)

    def read_api_key_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            logging.error(f"API Key file not found: {filename}")
            return None

    def fetch_weather_and_forecast(self, city):
        if self.api_key is None:
            # Handle missing API key
            return None, None

        current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"


        try:
            current_response = requests.get(current_weather_url).json()
            lat, lon = current_response['coord']['lat'], current_response['coord']['lon']
            forecast_response = requests.get(forecast_url.format(lat, lon, self.api_key)).json()
            
            print("-----------------Current Response----------------------")
            print(current_response)
            print("-----------------Forecast Response----------------------")
            print(forecast_response)
            
            if 'list' in forecast_response:
                daily_forecasts = []
                for daily_data in forecast_response['list'][:5]:  # Limit to the next 5 days
                    daily_forecasts.append({
                        "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
                        "min_temp": round(daily_data['main']['temp_min'] - 273.15, 2),
                        "max_temp": round(daily_data['main']['temp_max'] - 273.15, 2),
                        "description": daily_data['weather'][0]['description'],
                        "icon": daily_data['weather'][0]['icon']
                    })
            else:
                logging.error("No 'list' key in the forecast response.")
                return None, None

            weather_data = {
                "city": city,
                "temperature": round(current_response['main']['temp'] - 273.15, 2),
                "description": current_response['weather'][0]['description'],
                "icon": current_response['weather'][0]['icon'],
            }

            return weather_data, daily_forecasts
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
            return None, None
        except ValueError as e:
            logging.error(f"JSON parsing error: {e}")
            return None, None