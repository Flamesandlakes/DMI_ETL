# DMI_ETL
Extracting, transforming and loading data from DMI. Project at SPAC.

## Description
This repository provides a ETL pipeline to request data from APIs (such as DMI), parsing and transforming it, and subsequently store it in a local database. <br>
A Dockerfile and compose.yaml is provided to run this pipeline (alongside the database server) in an isolated environment. 

## Setup
**Setting up the database**\
Install Docker such that you can run "docker" commands.

Make your own config.txt file and fill it out, following the example in config_example.txt. Place the file outside of the src folder.

**Run and Build:**\
Download uv
```
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Run and build
```
    uv run dmi-etl
``` 
Use Docker to compose your container, which will setup an environment for the PostgreSQL server. 
<br><br>
It will also run main.py as part of the setup, which will extract data from DMI, transform it and load it into the server.
```
    docker compose up
```
Use pgAdmin4[^1], or a similar application (such as the Database tool from the PostgreSQL VSCode extension), to interface with the server.
<br><br>
When connecting to the server, use localhost (as the host) and port 5433. The user and password should likewise match your config.txt file (assuming that they are what the server accepts as valid).

## Software overview

The three steps of ETL, i.e. extraction, transformation and loading, are represented in these three respective files: extract.py, transform.py and DB_operations.py.
* dmi_etl.main:
    - Executes the ETL pipeline based on the functions imported from the the following Python files. 
    - The primary user interface of this repository is provided by main.py. When you run compose[^2], main.py will be executed.
* dmi_etl.extract:
    - Functions to handle and extract API call responses, without and with defined parameters.
* dmi_etl.transform:
    - Functions to parse and transform the received data into a streamlined format compatible with the database structure
* dmi_etl.DB_operations:
    - Functions to connect to the database, to setup the tables in the databasse, and to load data into the tables.
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


[^1]: pgAdmin4 version 9.17 is recommended. Version 9.18 requires a workaround (see: https://github.com/pgadmin-org/pgadmin4/issues/10437)
[^2]: "docker compose up" in terminal