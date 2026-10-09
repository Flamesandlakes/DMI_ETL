from dmi_etl.DB_operations import *
from dmi_etl.table_setup import create_parameter_table_query, create_readings_table_query, create_station_table_query
from unittest.mock import Mock
from unittest.mock import patch
from decimal import Decimal
#from datetime import date, time
import datetime
import os
import unittest


 #test behavior against a real database
class TestDBOperationsIntegrated(unittest.TestCase):

    #INTEGRATION TEST: LAV CONNECTION TIL RIGTIG DB, UDFØRE OPERATIONER, ASSERT, RYD OP
    #test at der er blevet sat noget ind i tabellen (load)
    #lav tabel, lav sql query (via cursor objekt) til at teste at tabellen eksisterer efter du har lavet dem, og så slet tabellen bagefter (create_tables)
    #test that the tables have actually been made

    def setUp(self):
        #change/mock env variables during test
        self.patched_env = patch.dict(os.environ, {"DB_NAME":"weatherdb_test"}) #rest of settings come from config.txt
        self.patched_env.start() #put DB_NAME into os.environ

    
    def tearDown(self):
        engine = get_engine()
        connection = engine.raw_connection()
        cursor = connection.cursor()
        #delete tables
        cursor.execute("DROP TABLE IF EXISTS readings_data")
        cursor.execute("DROP TABLE IF EXISTS parameter_data")
        cursor.execute("DROP TABLE IF EXISTS stations_data")
        
        #commit changes
        connection.commit()

        #close down connection
        cursor.close()
        connection.close()
        engine.dispose()

        self.patched_env.stop() #reset os.environ as it was before
        

    def test_commit_to_postgres_tables_commited(self):
        commit_to_postgres()

        engine = get_engine()
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables") #look in postgres' table over tables. Each row is one table
        tables = []
        for row in cursor.fetchall():  #fetches all the rows of a query result. It returns all the rows as a list of tuples
            tables.append(row[0]) #append first element of tuple
        cursor.close()
        connection.close()
        engine.dispose()
        assert "parameter_data" in tables
        assert "readings_data" in tables
        assert "stations_data" in tables
        

    def test_load_stations_into_db(self):
        engine = get_engine()
        connection = engine.raw_connection()
        cursor = connection.cursor()
        dummy_stations = [
            {"stationId": "01230", "longitude": 12.655, "latitude": 55.610},
            {"stationId": "01234", "longitude": 9.888, "latitude": 57.000},
            {"stationId": "00001", "longitude": 10.133, "latitude": 56.930}
        ]
        try:
            create_tables(cursor) #make tables
            load_stations(dummy_stations, cursor)
            cursor.execute("SELECT * FROM stations_data") #read tables
            result = cursor.fetchall()
            assert len(result) == 3
            expected = [('01230', Decimal('12.655'), Decimal('55.610')), 
                        ('01234', Decimal('9.888'), Decimal('57.000')), 
                        ('00001', Decimal('10.133'), Decimal('56.930'))]

            self.assertEqual(result, expected)
        finally:
            cursor.close()
            connection.close()
            engine.dispose()


    def test_load_parameter_into_db(self):
        engine = get_engine()
        connection = engine.raw_connection()
        cursor = connection.cursor()
        # dummy data for load_parameter
        dummy_parameters = [
            {"name": "temp", "unit": "Celsius", "frequency": "1h"},
            {"name": "humidity", "unit": "percent", "frequency": "1h"},
        ]
        try:
            create_tables(cursor) #make tables
            load_parameter(dummy_parameters, cursor)
            cursor.execute("SELECT * FROM parameter_data") #read tables
            result = cursor.fetchall()
            assert len(result) == 2

            expected =[('temp', 'Celsius', '1h'), 
                       ('humidity', 'percent', '1h')]
            
            self.assertEqual(result, expected)
        finally:
            cursor.close()
            connection.close()
            engine.dispose()



    def test_load_readings_into_db(self):
        engine = get_engine()
        connection = engine.raw_connection()
        cursor = connection.cursor()
        dummy_stations = [
            {"station_id": "01230", "longitude": 12.655, "latitude": 55.610},
            {"station_id": "01234", "longitude": 9.888, "latitude": 57.000},
            {"station_id": "00001", "longitude": 10.133, "latitude": 56.930}
        ]
        dummy_parameters = [
            {"name": "temp", "unit": "Celsius", "frequency": "1h"},
            {"name": "humidity", "unit": "percent", "frequency": "1h"},
        ]
        dummy_readings = [
            {"ParameterName": "temp", "ParameterValue": 12.3, "stationId": "01230",
            "Time": "12:00:00", "Date": "2026-10-01"},
        ]

        try:
            create_tables(cursor) #make tables
            load_parameter(dummy_parameters, cursor)
            load_stations(dummy_stations, cursor)

            load_readings(dummy_readings, cursor)
            cursor.execute("SELECT * FROM readings_data") #read tables
            result = cursor.fetchall()
            assert len(result) == 1
            expected = [('temp', Decimal('12.30'), 1, '01230', datetime.time(12, 0), datetime.date(2026, 10, 1))]
            self.assertEqual(result, expected)
        finally:
            cursor.close()
            connection.close()
            engine.dispose()





#--------------------------------------------------------------------------------------------------------------

class TestDBOperations(unittest.TestCase):

    #test that correct url string has been made
    #set env variables whilst test is running.
    @patch.dict(os.environ, {"DB_USER":"testuser", "DB_PASSWORD":"testpw","DB_HOST":"testhost",
                             "DB_PORT":"1234", "DB_NAME":"testdb"})
    #assert the url from get_engine is created correctly
    def test_get_engine_URL_string(self):
        engine = get_engine()
        # assert engine.url.drivername=="postgresql"
        # assert engine.url.username=="testuser"
        # assert engine.url.password=="testpw"
        # assert engine.url.host=="testhost"
        # assert engine.url.port==1234
        # assert engine.url.database=="testdb"
        self.assertEqual(engine.url.render_as_string(hide_password=False), "postgresql://testuser:testpw@testhost:1234/testdb")
    

    #test that that correct calls are made inside of commit_to_postgres()
    #patching get_engine, replacing it with a mock such that evertthing after is also fake
    @patch("dmi_etl.DB_operations.get_engine")
    def test_commit_to_postgres_implementation(self, mock_get_engine):
        #make fake objects
        engine = mock_get_engine.return_value #what get_engine returns
        connection = engine.raw_connection.return_value #what .raw_connection() returns
        cursor = connection.cursor.return_value #what .cursor returns

        commit_to_postgres()

        #assert that the correct calls were made inside of commit_to_postgres()
        assert cursor.execute.call_count==3 #assert cursor.execute is called once for each of the tables made via SQL queries
        connection.commit.assert_called_once()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()


    #TILFØJ TEST TIL ERROR HANDLING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def test_commit_to_postgres_error_handling(self):
        pass


    def test_create_tables(self):
        cursor = Mock() #create fake cursor
        # engine = get_engine()
        # connection = engine.raw_connection()
        # cursor = connection.cursor()
        create_tables(cursor)

        assert cursor.execute.call_count ==3 #assert .execute() method was called 3 times - one for each table created
        
    def test_load_parameter(self):
        cursor = Mock()
        dummy_parameters = [
            {"name": "temp", "unit": "Celsius", "frequency": "1h"}, 
            {"name": "humidity", "unit": "percent", "frequency": "1h"},
        ]
        load_parameter(dummy_parameters,cursor)
        assert cursor.execute.call_count == 2

    def test_load_stations(self):
        cursor = Mock()
        dummy_stations = [
            {"stationId": "01230", "longitude": 12.655, "latitude": 55.610},
            {"stationId": "01234", "longitude": 9.888, "latitude": 57.000},
            {"stationId": "00001", "longitude": 10.133, "latitude": 56.930}
        ]
        load_stations(dummy_stations, cursor)
        assert cursor.execute.call_count ==3

    def test_load_readings(self):
        cursor = Mock()
        dummy_readings = [
            {"parameterId": "temp", "value": 12.3, "stationId": "01230",
            "observedTime": "12:00:00", "observedDate": "2026-10-01"}]
        load_readings(dummy_readings, cursor)
        assert cursor.execute.call_count ==1


if __name__ == '__main__':
    unittest.main()
