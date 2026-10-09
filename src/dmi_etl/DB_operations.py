# importing relevant packages
#import json
#import pandas as pd
#import requests
from sqlalchemy import create_engine, URL
import configparser
from dmi_etl.table_setup import create_parameter_table_query, create_readings_table_query, create_station_table_query
from pathlib import Path
import os

def get_engine():
    """
    read config.txt and return SQLAlchemy object and connect to db
    """
    # creating a Configparser object
    config = configparser.ConfigParser()
    # find and read the configuration file
    config.read(Path(__file__).parents[2] / "config.txt")

    # reading credentials from file
    username = os.getenv("DB_USER", config.get('Credentials', 'username'))
    host = os.getenv("DB_HOST", config.get('Credentials', 'host'))
    password = os.getenv("DB_PASSWORD", config.get('Credentials', 'password'))
    port = int(os.getenv("DB_PORT", config.get('Credentials', 'port')))
    db_name = os.getenv("DB_NAME", config.get('Credentials', 'db_name'))

    return create_engine(URL.create(
    "postgresql",
    username=username, password=password,
    host=host, port=int(port), database=db_name,
    ))


def create_tables(cursor):
    """
    creating the table using the cursor
    """
    queries = [create_station_table_query,create_parameter_table_query,create_readings_table_query]
    for q in queries:
        cursor.execute(q)



def commit_to_postgres():
    """
    Function to save the data into a PostgreSQL database
    """

    engine = get_engine()
    # a raw database connection that allows direct interaction with the database
    connection = engine.raw_connection()

    # the cursor allows us to execute queries and retrieve results from the database
    cursor = connection.cursor()

    create_tables(cursor)


    # committing the current transaction to the database
    connection.commit()
    # closing the cursor
    cursor.close()
    # closing the connection
    connection.close()


def load_stations(dict_list, cursor):
    """
    Insert data into stations_data table
    Args: a list of dictionaries where each dictionary is one reading
    """
    for reading in dict_list:
        #load stations
        cursor.execute("INSERT INTO stations_data(station_id, longitude, latitude) VALUES (%s, %s, %s) ON CONFLICT (station_id) DO NOTHING",
        (reading["stationId"], reading["longitude"], reading["latitude"]),
        )


def load_parameter(dict_list, cursor):
    """
    Insert data into parameter_data table
    Args: a list of dictionaries where each dictionary is one reading
    """
    for reading in dict_list:
       # load parameter
        cursor.execute("INSERT INTO parameter_data(name, unit, frequency) VALUES (%s, %s, %s) ON CONFLICT(name) DO NOTHING",
                       (reading["name"], reading["unit"], reading["frequency"]),
        )

def load_readings(dict_list, cursor):
    """
    Insert data into readings_data table
    Args: a list of dictionaries where each dictionary is one reading
    """
    for reading in dict_list:
        # load readings
        cursor.execute("INSERT INTO readings_data(parameter_name, value, station_id, time, date) VALUES(%s, %s, %s, %s, %s)",
                       (reading["parameterId"], reading["value"], reading["stationId"], reading["observedTime"], reading["observedDate"]),
        )


if __name__ == "__main__":

    # dummy data for testing the station part of load_data
    dummy_stations = [
        {"stationId": "01230", "longitude": 12.655, "latitude": 55.610},
        {"stationId": "01234", "longitude": 9.888, "latitude": 57.000},

        {"stationId": "00001", "longitude": 10.133, "latitude": 56.930}
    ]

    # dummy data for load_parameter
    dummy_parameters = [
        {"name": "temp", "unit": "Celsius", "frequency": "1h"},
        {"name": "humidity", "unit": "percent", "frequency": "1h"},
    ]

    # dummy data for load_readings
    dummy_readings = [
        {"parameterId": "temp", "value": 12.3, "stationId": "01230",
         "time": "12:00:00", "date": "2026-10-01"},

        {"parameterId": "humidity", "value": 81.5, "stationId": "01230",
         "time": "12:00:00", "date": "2026-10-01"},

        {"parameterId": "temp", "value": 11.8, "stationId": "01234",
         "time": "12:00:00", "date": "2026-10-01"},

        {"parameterId": "temp", "value": 13.1, "stationId": "00001",
         "time": "13:00:00", "date": "2026-10-01"},
    ]


    engine = get_engine()
    # a raw database connection that allows direct interaction with the database
    connection = engine.raw_connection()
    # the cursor allows us to execute queries and retrieve results from the database
    cursor = connection.cursor()
    create_tables(cursor)

    #first load data into stations, then into parameter and then readings
    load_stations(dummy_stations, cursor)
    load_parameter(dummy_parameters, cursor)
    load_readings(dummy_readings, cursor)

    connection.commit()

