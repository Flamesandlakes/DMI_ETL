# importing relevant packages
import json
import pandas as pd
import requests
from sqlalchemy import create_engine, URL
import configparser
from dmi_etl.table_setup import create_parameter_table_query, create_readings_table_query, create_station_table_query

from pathlib import Path



# Defining a function to save the data into a PostgreSQL database
def commit_to_postgres():

    # creating a Configparser object
    config = configparser.ConfigParser()
    # find and read the configuration file
    config.read(Path(__file__).parents[2] / "config.txt")

    # reading credentials from file
    username = config.get('Credentials', 'username')
    host = config.get('Credentials', 'host')
    password = config.get('Credentials', 'password')
    port = config.get('Credentials', 'port')
    db_name = config.get('Credentials', 'db_name')
    
    #make SQLAlchemy object to connect to database.
    engine = create_engine(URL.create(
    "postgresql",
    username=username, password=password,
    host=host, port=int(port), database=db_name,
    ))

    # a raw database connection that allows direct interaction with the database
    connection = engine.raw_connection()

    # the cursor allows us to execute queries and retrieve results from the database
    cursor = connection.cursor()

    # creating the table using the cursor
    queries = [create_station_table_query,create_parameter_table_query,create_readings_table_query]
    for q in queries:
        cursor.execute(q)





    # committing the current transaction to the database
    connection.commit()

    # closing the cursor
    cursor.close()
    # closing the connection
    connection.close()



