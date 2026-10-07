# DMI_ETL
Extracting, transforming and loading data from DMI. Project at SPAC.


**Setting up database**\
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
Use Docker to compose your container, which will setup an environment for the PostgreSQL server. <br>It will also run main.py as part of the setup, which will extract data from DMI, transform it and load it into the server.
```
    docker compose up
```
Use pgAdmin4 (version 9.17), or a similar application (such as the Database tool from the PostgreSQL VSCode extension), to interface with the server.
<br>When connecting to the server, use localhost (as the host) and port 5433. The user and password should likewise match your config.txt file (assuming that they are what the server accepts as valid).
