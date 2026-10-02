# sql syntax to create the table that would hold data

create_readings_table_query = """
    CREATE TABLE IF NOT EXISTS readings_data(
                parameter_name text,
                value decimal(6,2),
                reading_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                station_id text,
                time time,
                date date,
                CONSTRAINT fk_stations
                FOREIGN KEY (station_id) 
                REFERENCES stations_data(station_id),
                CONSTRAINT fk_parameter
                FOREIGN KEY (parameter_name)
                REFERENCES parameter_data(name),
                CONSTRAINT unique_reading UNIQUE (station_id, parameter_name, date, time)
                )
            """

create_station_table_query = """ 
    CREATE TABLE IF NOT EXISTS stations_data(
                station_id text PRIMARY KEY,
                longitude decimal(6,3),
                latitude decimal(6,3)
                )
            """

create_parameter_table_query = """ 
    CREATE TABLE IF NOT EXISTS parameter_data(
                name text PRIMARY KEY,
                unit text,
                frequency text
                ) 
            """