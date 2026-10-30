# DMI_ETL
Extracting, transforming and loading data from DMI. Project at SPAC.

## Description
This repository provides a ETL pipeline to request data from APIs (such as DMI), parsing and transforming it, and subsequently store it in a local database. <br>
Docker is used to run and containerize the PostgreSQL database server in an isolated environment, and a compose.yaml file is provided. The pipeline itself runs locally with uv.

## Setup
**Setting up the database**\
Install Docker such that you can run "docker" commands.

Make your own config.txt file and fill it out, following the example in config_example.txt, and matching the information in the compose.yaml file. Place the file at the root directory.

Optional: If you want to retrieve observations from SPAC's climate sensors, you must make your own own .env file and fill it out, in accordance with the example shown in .env_example.txt. 

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

When running the pipeline, a GUI pops up where you can input select api source and a corresponding set of options to specify the data that the pipeline should extract.
<br><br>
Use pgAdmin4[^1], or a similar application (such as the Database tool from the PostgreSQL VSCode extension), to interface with the server.
<br><br>
When connecting to the server, use `host=localhost` and `port=5432`. The user and password should match the information in the compose.yaml file.


To stop the database, use
```
    docker compose down
```

**Locally host an API with access to your database** 
To enable other users on the same WiFi network to interface with your database, use
```
    uv run src/dmi_etl/api.py
```
The terminal will show the HTTP address that can be used to access the API with. 
The /docs subdomain webpage on this address provides an overview of the possible CRUD methods.
Users must login with a valid username and password. The user_db dictionary located in api.py can be modified, both in terms of users, their login and their access. Note that the password must be hashed with the Argon2 hashing algorithm[^3]. 

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

The three steps of ETL, i.e. extraction, transformation and loading, are represented in these three respective files: <b>extract.py, transform.py and DB_operations.py</b>. Additional functionality relies on: main.py, interface.py, table_setup.py, api.py and api_auth.py.
* dmi_etl.main:
    - Executes the ETL pipeline based on the functions imported from the following Python files. 
    - The primary user interface of this repository is provided when main.py is executed.
* dmi_etl.interface:
    - The primary user interface which can be used to select which API to extract data from, and in that regard, specify what data to request.
* <b>dmi_etl.extract</b>:
    - Functions to handle and extract API call responses, without and with defined parameters.
* <b>dmi_etl.transform</b>:
    - Functions to parse and transform the received data into a streamlined format compatible with the database structure
* <b>dmi_etl.DB_operations</b>:
    - Functions to connect to the database, to setup the tables in the database, and to load data into the tables.
* dmi_etl.table_setup
    - String objects that defines the structure of the tables. These tables are imported in DB_operations and are used to setup the tables in the database.
* dmi_etl.api
    - Script that is used to host an API to your own local database. Includes functions and classes that determine the response to CRUD calls to the API's CRUD including the required access.
* dmi_etl.api_auth
    - Functions pertaining to authentication and authorization for usage of the API run from api.py.  


## Use Cases
There are overall three high-level use cases: 1. Getting data through the ETL pipeline, 2. hosting access to the database through an API, and 3. interacting with said API.
![Use Case UML for the DMI ETL Project](https://github.com/Flamesandlakes/parser/blob/main/images/UML for DMI ETL project_Use Case diagram v2.usecase.png)

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
    - dotenv>=0.9.9


[^1]: pgAdmin4 version 9.17 is recommended. Version 9.18 requires a workaround (see: https://github.com/pgadmin-org/pgadmin4/issues/10437)
[^2]: "docker compose up" in terminal
[^3]: However the exact hashing algorithm may be subject to change, due to external changes in security standards.