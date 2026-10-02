# DMI_ETL
Extracting, transforming and loading data from DMI. Project at SPAC.


**Setting up database**\
Download PostgreSQL and follow the steps here: https://www.w3schools.com/postgresql/postgresql_install.php

Connect to database by following the steps here (using pgadmin4): https://www.w3schools.com/postgresql/postgresql_pgadmin4.php

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

