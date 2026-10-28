# sql syntax to create the table that would hold data
create_schema_query = "CREATE SCHEMA IF NOT EXISTS climate;"
 
create_readings_table_query = """
    CREATE TABLE IF NOT EXISTS climate.readings_data(
                parameter_name text,
                value decimal(10,2),
                reading_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                station_id text,
                time time,
                date date,
                CONSTRAINT fk_stations
                FOREIGN KEY (station_id) 
                REFERENCES climate.stations_data(station_id),
                CONSTRAINT fk_parameter
                FOREIGN KEY (parameter_name)
                REFERENCES climate.parameter_data(name),
                CONSTRAINT unique_reading UNIQUE (station_id, parameter_name, date, time)
                )
            """

create_station_table_query = """ 
    CREATE TABLE IF NOT EXISTS climate.stations_data(
                station_id text PRIMARY KEY,
                longitude decimal(6,3),
                latitude decimal(6,3),
                location_name text
                )
            """

create_parameter_table_query = """ 
    CREATE TABLE IF NOT EXISTS climate.parameter_data(
                name text PRIMARY KEY,
                unit text,
                frequency text
                ) 
            """

# define roles and permissions
define_role_perm = "CREATE ROLE anon_user NOLOGIN;" \
"GRANT USAGE ON SCHEMA climate TO anon_user;" \
"GRANT SELECT ON SCHEMA climate TO anon_user;" \
"CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'mysecretpassword';" \
"GRANT anon_user TO authenticator;"
