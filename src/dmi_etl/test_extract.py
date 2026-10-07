import unittest
from dmi_etl.extract import *

class Test_get_data(unittest.TestCase):
    def test_tom_url(self):
        get_data("")
        pass
    def test_ikke_url(self):
        get_data("blabla")
        pass

    def test_http(self):
            get_data("http://opendataapi.dmi.dk/v2/metObs/collections/observation/items")
            pass

    def test_https_stavefejl1(self):
             get_data("htp://opendataapi.dmi.dk/v2/metObs/collections/observation/items")
             pass

    def test_kommando_print(self):
             #get_data("print("hahahaha")")
             pass
    def test_url_findes_ikke(self):
                get_data("http://opendataapi.dmi.dk/v2/dfgmetObs/collections/observation/items")
                pass
    

class Test_get_data_with_params(unittest.TestCase):
    def test_get_data_with_params(self):
        pass

class Test_get_station_data(unittest.TestCase):
    def test_get_station_data(self):
        pass
