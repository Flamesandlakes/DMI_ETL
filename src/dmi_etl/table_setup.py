# sql syntax to create the table that would hold our data

create_readings_table_query = """ 
    CREATE TABLE IF NOT EXISTS readings_data(
                parameter text,
                value decimal(6,2),
                stationID integer,
                time time,
                date date,
                CONSTRAINT fk_reading
                FOREIGN KEY (stationID) 
                REFERENCES stations(stationID)
                )
            """

create_station_table_query = """ 
    CREATE TABLE IF NOT EXISTS stations(
                stationID integer PRIMARY KEY,
                name text,
                address text,
                longitude decimal(6,3),
                latitude decimal(6,3)
                )
            """

create_parameter_table_query = """ 
    CREATE TABLE IF NOT EXISTS parameter(
                name text PRIMARY KEY,
                unit text,
                frequency text
                ) 
            """