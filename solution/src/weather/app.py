#!/usr/bin/python

from flask import Flask, render_template
from markupsafe import escape
from opentelemetry import trace
import requests
import waitress

from logger import initLogger
from db import *
import os


app = Flask(__name__)

# Get Service URLs from environment variables
WEATHER_PORT = os.getenv("WEATHER_PORT", "8080")
COORDINATES_SERVICE_URL = os.getenv("COORDINATES_SERVICE_URL", "https://nominatim.openstreetmap.org/search?format=json&q=")
FORECAST_URL = os.getenv("FORECAST_URL", "http://forecast:9090/forecast?")


@app.route("/weather/<location>/<country>", methods=["GET"])
def get_weather(location, country):
  location = f"{escape(location)}"
  country = f"{escape(country)}"
  if not location or not country:
    return render_template("error.html", message="Location and Country are required"), 400
  
  logger.info("Received request to get weather data", extra={"location": location, "country": country})

  current_span = trace.get_current_span()
  current_span.set_attributes({
    "app.city": location,
    "app.country": country
  })

  # Check if coordinates are already in the database
  coordinates = get_coordinates_from_db(location, country)
  if coordinates:
    latitude, longitude = coordinates
    return get_weather_by_coordinates(latitude, longitude)
  else:
    return get_coordinates_from_coordinates_service(location, country)


def save_coordinates(location, country, cities):
  for city in cities:
    lat = city.get("lat")
    lon = city.get("lon")
    insert_coordinates_into_db(location, country, lat, lon)


def get_coordinates_from_coordinates_service(location, country):
  try:
    headers = {
        "User-Agent": "otel-lab/1.0"
    }
    # Resolve coordinates from the location name
    coordinates_response = requests.get(f"{COORDINATES_SERVICE_URL}{location},{country}", headers=headers)
    if coordinates_response.status_code != 200:
      return render_template("error.html", message="Failed to resolve coordinates"), coordinates_response.status_code

    coordinates = coordinates_response.json()

    # Filter results to include any address type that contains "city"
    cities = [entry for entry in coordinates if "city" in entry.get("addresstype", "")]

    if not cities:
      # Filter results to include any address type that contains "municipality"
      cities = [entry for entry in coordinates if "municipality" in entry.get("addresstype", "")]
      if not cities:
        return render_template("error.html", message="No cities or municipalities found for the given location"), 404

    # Insert cities into the database
    save_coordinates(location, country, cities)

    if len(cities) == 1:
      selected_city = cities[0]
    else:
      logger.info("Multiple cities found for the given location", extra={"cities": cities})
      # If multiple cities found, return the list of cities to
      # the user to choose from
      city_options = {
          str(index + 1): {
          "name": city["display_name"],
          "link": f"http://localhost:8080/weather/{city['lat']}/{city['lon']}"
          }
          for index, city in enumerate(cities)
      }
      return render_template("multiple_cities.html", cities=city_options), 300

    latitude = selected_city.get("lat")
    longitude = selected_city.get("lon")
    
    return get_weather_by_coordinates(latitude, longitude)
  except Exception as e:
    return render_template("error.html", message=str(e)), 500


def convert_daylight_duration(daylight_duration):
  with tracer.start_as_current_span("convert_daylight") as span:
    span.set_attribute("daylight_duration", daylight_duration)
    hours = int(daylight_duration // 3600)
    minutes = int ((daylight_duration % 3600) // 60)

    span.set_status(trace.Status(trace.StatusCode.OK))
    return f"{hours}h {minutes}min"


@app.route("/weather/coordinates/<latitude>/<longitude>", methods=["GET"])
def get_weather_by_coordinates(latitude, longitude):
  latitude = f"{escape(latitude)}"
  longitude = f"{escape(longitude)}"
  if not latitude or not longitude:
    return render_template("error.html", message="Latitude and longitude are required"), 400

  logger.info("Received request to get weather data by coordinates", extra={"latitude": latitude, "longitude": longitude})

  try:
    # Fetch forecast data using the provided coordinates
    forecast_response = requests.get(f"{FORECAST_URL}latitude={latitude}&longitude={longitude}")
    if forecast_response.status_code != 200:
      return render_template("error.html", message="Failed to fetch forecast data"), forecast_response.status_code

    forecast_data = forecast_response.json()

    daylight_duration = convert_daylight_duration(forecast_data['daily']['daylight_duration'][0])

    # Return the weather data to the user
    return render_template("weather.html", latitude=latitude, longitude=longitude, daylight_duration=daylight_duration, weather_data=forecast_data)
  except Exception as e:
    return render_template("error.html", message=str(e)), 500


if __name__ == "__main__":
  service_name = os.getenv("OTEL_SERVICE_NAME")
  tracer = trace.get_tracer_provider().get_tracer(service_name)

  logger = initLogger(service_name)
  logger.info(f"Starting weather service on port {WEATHER_PORT}")
  waitress.serve(app, host="0.0.0.0", port=WEATHER_PORT)
