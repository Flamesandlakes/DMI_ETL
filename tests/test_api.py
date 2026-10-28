from dmi_etl.DB_operations import *
from dmi_etl.api import *
from dmi_etl.api import app
from dmi_etl.api_auth import UserInDB
from unittest.mock import patch
from fastapi.testclient import TestClient

import datetime
import os
import unittest



class TestAPI(unittest.TestCase):

    def setUp(self):
        #change/mock env variables during test
        self.patched_env = patch.dict(os.environ, {"DB_NAME":"weatherdb_test"}) #rest of settings come from config.txt
        self.patched_env.start() #put DB_NAME into os.environ

        #make engine for this test db not from api.py
        self.engine = get_engine()
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        create_tables(cursor)
        #commit changes
        connection.commit()
        #close down connection
        cursor.close()
        connection.close()

        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)


        def override_get_db():
            db = TestSessionLocal()
            try:
                yield db
            finally:
                db.close() #close down the session

        app.dependency_overrides[get_db] = override_get_db #use override_get_db instead of get_db

        self.client = TestClient(app)

        #create and return a UserInDB object
        def override_user():
            return UserInDB(username="tester", hashed_password="x",
                            access=["parameters_admin", "stations_admin", "readings_admin"])

        app.dependency_overrides[get_current_active_user] = override_user #use override_user instead of get_current_active_user

    def tearDown(self):
        #remove the override
        app.dependency_overrides.clear()

        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        #delete tables
        cursor.execute("DROP TABLE IF EXISTS climate.readings_data")
        cursor.execute("DROP TABLE IF EXISTS climate.parameter_data")
        cursor.execute("DROP TABLE IF EXISTS climate.stations_data")
        cursor.execute("DROP TABLE IF EXISTS climate.station_data")        
        connection.commit()
        cursor.close()
        connection.close()
        self.engine.dispose()

        self.patched_env.stop()


    def test_create_read_parameter(self):
        test_param = {
            "name": "tests_1",
            "unit":"test unit",
            "frequency":"test frequency"
            }
        # send request as a client by giving it URL and body
        self.client.post("/parameters/", json=test_param)
        # Send a GET request to the root path "/"
        response = self.client.get("/parameters/tests_1")
        # Assert that the HTTP status code is 200 (OK)
        assert response.status_code == 200
        assert response.json() == test_param        


    def test_read_parameter_not_exist(self):
        # Send a GET request to the root path "/"
        response = self.client.get("/parameters/parameter_not_exist")
        # Assert that the HTTP status code is 404
        assert response.status_code == 404


    def test_delete_parameter(self):
        test_param = {
            "name": "tests_1",
            "unit":"test unit",
            "frequency":"test frequency"
            }
        self.client.post("/parameters/", json=test_param)
        
        response = self.client.delete("/parameters/tests_1")
        assert response.status_code == 204


    def test_delete_parameter_not_exist(self):
        response = self.client.delete("/parameters/9999")
        assert response.status_code == 404


    def test_update_parameter(self):
        test_param = {
            "name": "tests_1",
            "unit":"test unit",
            "frequency":"test frequency"
            }
        self.client.post("/parameters/", json=test_param)
        updated_param={
            #"name": "string",
            "unit": "updated unit",
            "frequency": "updated frequency"
            }
        response = self.client.put("/parameters/tests_1/", json=updated_param)
        assert response.status_code == 200
        assert response.json() == {
            "name": "tests_1",
            "unit": "updated unit",
            "frequency": "updated frequency"
            }

    def test_update_parameter_not_exist(self):
        # test_param = {
        #     "name": "tests_1",
        #     "unit":"test unit",
        #     "frequency":"test frequency"
        #     }
        # self.client.post("/parameters/", json=test_param)
        updated_param={
            #"name": "string",
            "unit": "updated unit",
            "frequency": "updated frequency"
            }
        response = self.client.put("/parameters/not_exist/", json=updated_param)
        assert response.status_code == 404


        

    def test_create_read_station(self):
        test_station = {
            "station_id": "1234", 
            "longitude":11.112, 
            "latitude":11.123, 
            "location_name": "test1234"
            }
        self.client.post("/stations/", json=test_station)
        response = self.client.get("/stations/1234")

        assert response.status_code == 200
        assert response.json() == test_station


    def test_read_station_not_exist(self):
        response = self.client.get("/stations/9999")
        assert response.status_code == 404


    def test_delete_station(self):
        test_station = {"station_id": "1234", "longitude":11.112, "latitude":11.123, "location_name": "test1234"}
        self.client.post("/stations/", json=test_station)
        response = self.client.delete("/stations/1234")
        assert response.status_code == 204


    def test_delete_station_not_exist(self):
        response = self.client.delete("/stations/9999")
        assert response.status_code == 404


    def test_update_station(self):
        test_station = {
            "station_id": "1234", 
            "longitude":11.111, 
            "latitude":11.222, 
            "location_name": "test1234"
            }
        update_station = {
            #"station_id": "1234", 
            "longitude":22.222, 
            "latitude":33.333, 
            "location_name": "updated name"
            }
        self.client.post("/stations/", json=test_station)
        response = self.client.put("/stations/1234", json=update_station)

        assert response.status_code == 200
        assert response.json() == {
            "station_id": "1234", 
            "longitude":22.222, 
            "latitude":33.333, 
            "location_name": "updated name"
            }

    def test_update_station_not_exist(self):
        update_station = {
            #"station_id": "1234", 
            "longitude":22.222, 
            "latitude":33.333, 
            "location_name": "updated name"
            }
        response = self.client.put("/stations/1234", json=update_station)
        assert response.status_code == 404