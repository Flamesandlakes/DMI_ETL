create_readings_table_query = """ 
    CREATE TABLE readings_data(
                parameter text,
                value decimal(p,s),
                CONSTRAINT stationID FOREIGN KEY REFERENCES stations(stationID),
                time time,
                date date
                ) 
            """

create_station_table_query = """ 
    CREATE TABLE stations(
                stationID integer PRIMARY KEY,
                name text,
                address text,
                longitude decimal(p,s),
                latitude decimal(p,s)
                ) 
            """

create_parameter_table_query = """ 
    CREATE TABLE parameter(
                name text PRIMARY KEY,
                unit text,
                frequency text,
                ) 
            """