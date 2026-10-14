# DMI_ETL
Extracting, transforming and loading data from DMI. Project at SPAC.

## Description
This repository provides a ETL pipeline to request data from APIs (such as DMI), parsing and transforming it, and subsequently store it in a local database. <br>
Docker is used to run and containerize the PostgreSQL database server in an isolated environment, and a compose.yaml file is provided. The pipeline itself runs locally with uv.

## Setup
**Setting up the database**\
Install Docker such that you can run "docker" commands.

Make your own config.txt file and fill it out, following the example in config_example.txt, and matching the information in the compose.yaml file. Place the file at the root directory.

**Run and Build:**\
Download uv for windows:
```
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
For MacOS and Linux, use: https://docs.astral.sh/uv/getting-started/installation/#installation-methods 

<br><br>
Use Docker to compose your container, which will setup an environment to start the PostgreSQL server.  Use the following command to start the database and fetch the image:
<br><br>
```
    docker compose up -d
```
To run the pipeline, use:
```
    uv run src/dmi_etl/main.py
``` 

When running the pipeline, a GUI pops up where you can input data, stations and dates to specify the data that the pipeline should extract.
<br><br>
Use pgAdmin4[^1], or a similar application (such as the Database tool from the PostgreSQL VSCode extension), to interface with the server.
<br><br>
When connecting to the server, use `host=localhost` and `port=5432`. The user and password should match the information in the compose.yaml file.


To stop the database, use
```
    docker compose down
```


**Run tests and code coverage**\
When the container starts for the first time, the SQL script db_init/create_test_db.sql runs automatically. 
It creates the test database weatherdb_test, which the tests use.
```
uv run coverage run -m unittest discover
```
```
uv run -m coverage report -m
```
If weatherdb_test does not exist, run `docker compose down` and then `docker compose up -d`


## Software overview

The three steps of ETL, i.e. extraction, transformation and loading, are represented in these three respective files: extract.py, transform.py and DB_operations.py.
* dmi_etl.main:
    - Executes the ETL pipeline based on the functions imported from the following Python files. 
    - The primary user interface of this repository is provided by main.py.
* dmi_etl.extract:
    - Functions to handle and extract API call responses, without and with defined parameters.
* dmi_etl.transform:
    - Functions to parse and transform the received data into a streamlined format compatible with the database structure
* dmi_etl.DB_operations:
    - Functions to connect to the database, to setup the tables in the database, and to load data into the tables.
* dmi_etl.table_setup
    - String objects that defines the structure of the tables. These tables are imported in DB_operations and are used to setup the tables in the database.


### Dependencies

* Python >= 3.13
* Packages:
    - datetime>=6.0
    - configparser>=7.2.0
    - pandas>=3.0.6
    - psycopg[binary]>=3.3.6
    - requests>=2.34.2
    - sqlalchemy>=2.1.1
    - coverage>=7.16.2
    - customtkinter>=6.0.0
    - tkcalendar>=1.6.1


[^1]: pgAdmin4 version 9.17 is recommended. Version 9.18 requires a workaround (see: https://github.com/pgadmin-org/pgadmin4/issues/10437)
[^2]: "docker compose up" in terminal