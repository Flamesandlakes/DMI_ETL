import unittest
from dmi_etl.extract import *
from unittest.mock import patch

class Test_get_data(unittest.TestCase):
    @patch("dmi_etl.extract.requests.get")
    def test_forsoeg(self, mock_get):
        mock_data = {
            "stationId": "06188",
            "value": 12.5,
        }

        mock_get.return_value.json.return_value = mock_data
        resultat = get_data("https://findesikke.dk")
        pass
        self.assertEqual(resultat, mock_data)


class Test_get_data_with_params(unittest.TestCase):
    def test_get_data_with_params(self):
        pass

class Test_get_station_data(unittest.TestCase):
    def test_get_station_data(self):
        pass
