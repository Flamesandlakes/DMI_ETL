
import unittest
import src.dmi_etl.Transform as Transform

"""Example data for testing"""
testdata = {
  "type": "FeatureCollection",
  "features": [
    {
      "geometry": {
        "coordinates": [
          10.4398,
          55.3088
        ],
        "type": "Point"
      },
      "id": "02453972-f3fe-72b5-8d30-3f24a89107d9",
      "type": "Feature",
      "properties": {
        "created": "2023-10-26T09:19:43.376959Z",
        "observed": "2023-10-26T09:20:00Z",
        "parameterId": "leav_hum_dur_past10min",
        "stationId": "06126",
        "value": 0.0
      }
    }
  ],
  "timeStamp": "2023-10-26T09:19:51Z",
  "numberReturned": 1,
  "links": [
    {
      "href": "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items?limit=1&sortorder=observed,DESC",
      "rel": "self",
      "type": "application/geo+json",
      "title": "This document"
    },
    {
      "href": "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items?limit=1&sortorder=observed,DESC&offset=1",
      "rel": "next",
      "type": "application/geo+json",
      "title": "Next set of results"
    }
  ]
}

"""Unit tests of getting functions"""
class test_getting_functions(unittest.TestCase):
    def test_of_get_location(self):
        self.assertEqual(Transform.Get_Location(testdata), [10.4398, 55.3088])

    def test_of_get_stationId(self):
        self.assertEqual(Transform.Get_StationId(testdata), "06126")
        
    def test_of_get_parameter(self):
        Parameter_Name, Parameter_Value = Transform.Get_Parameter(testdata)
        self.assertTrue(Parameter_Name == "leav_hum_dur_past10min" and Parameter_Value == 0.0)
        
    def test_of_get_date_and_time(self):
        test_date, test_time = Transform.Get_Date_And_Time(testdata)
        self.assertTrue(test_date == "2023-10-26" and test_time == "09:19:51")

"""Unit test of creating a dictionary"""
class test_make_dict(unittest.TestCase):
    testdict = Transform.Make_Dict_From_Data(testdata)
    
    def test_dict_len(self):
        self.assertTrue(len(self.testdict) == 7)
        
    def test_dict_longitude(self):
        self.assertEqual(self.testdict["Longitude"], 10.4398)

    def test_dict_latitude(self):
        self.assertEqual(self.testdict["Latitude"], 55.3088)

    def test_dict_stationId(self):
        self.assertEqual(self.testdict["stationId"], "06126")

    def test_dict_parameter_name(self):
        self.assertEqual(self.testdict["ParameterName"], "leav_hum_dur_past10min")

    def test_dict_parameter_value(self):
        self.assertEqual(self.testdict["ParameterValue"], 0.0)
    
    def test_dict_date(self):
        self.assertEqual(self.testdict["Date"], "2023-10-26")

    def test_dict_time(self):
        self.assertEqual(self.testdict["Time"], "09:19:51")


"""Unit test of list of dictionaries"""
class test_dictionaries_from_list(unittest.TestCase):
    testdict = Transform.Make_Dict_From_Data(testdata)
    testlist = [testdata,testdata,testdata]
    testlistdict = Transform.Make_Dicts_From_List(testlist)
    
    def test_of_list_of_dicts_length(self):
        self.assertEqual(len(self.testlistdict), 3)
        
    def test_list_first_entry(self):
        self.assertEqual(self.testdict, self.testlistdict[0])