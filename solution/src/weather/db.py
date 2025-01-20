#!/usr/bin/python

import logging
from markupsafe import escape
import psycopg2
import os

logger = logging.getLogger("weather")

POSTGRES_DB = os.getenv("POSTGRES_DB", "coordinates")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PWD = os.getenv("POSTGRES_PWD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "coordinates-db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_db_connection():
  return psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PWD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
  )

def get_coordinates_from_db(location, country):
  logger.info("Fetching coordinates from the database", extra={"location": location, "country": country})

  try:
    connection = get_db_connection()
    cursor = connection.cursor()

    try:      
      query = f"SELECT latitude, longitude FROM {POSTGRES_DB} WHERE city = %s AND country = %s;"
      cursor.execute(query, (location, country))

      result = cursor.fetchone()

      cursor.close()
      connection.close()
      return result
    except Exception as e:
      logger.error("Error fetching coordinates from the database", extra={"error": str(e)})
      return None
    
  except Exception as e:
    logger.error("Error accessing the database", extra={"error": str(e)})
    return None

def insert_coordinates_into_db(location, country, latitude, longitude):
  logger.info("Inserting coordinates into database", extra={"location": location, "country": country})
  try:
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
      query = f"INSERT INTO {POSTGRES_DB} (city, country, latitude, longitude) VALUES (%s, %s, %s, %s);"
      cursor.execute(query, (location, country, latitude, longitude))

      connection.commit()
      cursor.close()
      connection.close()
    except Exception as e:
      logger.error("Error inserting coordinates into the database", extra={"error": str(e)})
  except Exception as e:
    logger.error("Error accessing the database", extra={"error": str(e)})
