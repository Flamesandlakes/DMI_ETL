import unittest
from dmi_etl.extract import *
from dmi_etl.utility import Credentials
from unittest.mock import patch, MagicMock
class Test_get_data(unittest.TestCase):
    @patch("dmi_etl.extract.requests.get")
    def test_forsoeg(self, mock_get):
        mock_data = {
            "stationId": "06188",
            "value": 12.5,
        }

        mock_get.return_value.json.return_value = mock_data
        resultat = get_data("https://findesikke.dk")
        
        self.assertEqual(resultat, mock_data)


class Test_get_data_with_params(unittest.TestCase):
    @patch("dmi_etl.extract.requests.get")
    def test_get_data_with_params(self, mock_get):
        mock_data = {
            "stationId": "06188",
            "value": 12.5,
        }

        base_url = "https://findesikke.dk"
        parameters = {
            "stationId": "06188",
            "parameterId": "temp_mean_past1h"
        }

        mock_get.return_value.json.return_value = mock_data
        
        resultat = get_data_with_params(base_url, parameters)
        self.assertEqual(resultat, mock_data)


class Test_get_station_data(unittest.TestCase):
    @patch("dmi_etl.extract.requests.get")
    def test_get_station_data(self, mock_get):
        mock_data = {
            "type": "FeatureCollection",
            "features": [
            {
                "properties": {
                    "stationId": "06188",
                    "name": "Sjælsmark",
                }
            }
            ],
            "numberReturned": 1,
        }
        mock_get.return_value.json.return_value = mock_data

        resultat = get_station_data(["06188"])

        self.assertEqual(resultat, [mock_data])

class Test_get_data_from_api_with_credentials(unittest.TestCase):
    @patch("dmi_etl.extract.requests.get")
    def test_get_data_from_api(self, mock_get):
        mock_data = {'observationId': '9c6a6723-f8cf-4a12-b165-a854e2bd065e', 
                     'nodeId': '2c47284d-777b-44f0-bdeb-3d442f6a31b1', 
                     'instrumentId': 'BME280:75E99D2B', 
                     'instrumentModel': 'BME280', 
                     'sensor': 'temperature', 
                     'readingId': '818c1516-4c56-402c-9617-52d7759b0532', 
                     'value': 22.98187255859375, 
                     'timestamp': '2026-10-26T11:47:46.900728Z'}
                

        base_url = "https://findesikke.dk/api/v1/obs"

        mock_get.return_value.json.return_value = mock_data

        try:
            cred = Credentials()
        except Exception as _:
            cred = MagicMock()
        cred.spac_api_id = "someId"
        cred.spac_api_key= "someKey"

        resultat = get_data_from_api_with_credentials(base_url, {}, cred)
        #print(resultat)
        self.assertEqual(resultat, mock_data)

class Test_rate_constraint(unittest.TestCase):

    def test_count_call(self):
        test_ratefollower = RateConstraint()
        self.assertEqual(test_ratefollower.calls_so_far,0)
        test_ratefollower.count_call()
        self.assertEqual(test_ratefollower.calls_so_far,1)

    def test_sleep(self):
        test_ratefollower = RateConstraint(time_to_exceed = 1)
        test_ratefollower.calls_so_far = 500

        reference_time = test_ratefollower.reference_time
        test_ratefollower.count_call()
        new_time = time.time()
        self.assertEqual(test_ratefollower.calls_so_far,0)
        self.assertTrue(new_time - reference_time >= 1)
        self.assertNotEqual(reference_time, test_ratefollower.reference_time)
