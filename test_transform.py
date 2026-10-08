
import unittest
import src.dmi_etl.transform as Transform

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
    },
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
    },
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
        "stationId": "06127",
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

testdata2 = {
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

testdata3 = {
  "type": "FeatureCollection",
  "features": [],
  "timeStamp": "2026-10-08T09:50:54Z",
  "numberReturned": 0,
  "links": [
    {
      "href": "https://opendataapi.dmi.dk/v2/metObs/collections/station/items?stationId=06127",
      "rel": "self",
      "type": "application/geo+json",
      "title": "This document"
    }
  ]
}
parameterlist = ["properties.stationId", "properties.parameterId",  "properties.value", "properties.observed", "geometry"]


"""Unit tests of getting functions"""
class test_getting_functions(unittest.TestCase):
    def test_of_get_location(self):
        self.assertEqual(Transform.Get_Location(testdata["features"][0]), [10.4398, 55.3088])

    def test_of_get_stationId(self):
        self.assertEqual(Transform.Get_Parameter_From_Properties(testdata["features"][0],"stationId"), "06126")
        
    def test_of_get_parameter(self):
        Parameter_Name = Transform.Get_Parameter_From_Properties(testdata["features"][0],"parameterId")
        Parameter_Value = Transform.Get_Parameter_From_Properties(testdata["features"][0],"value")
        self.assertTrue(Parameter_Name == "leav_hum_dur_past10min" and Parameter_Value == 0.0)
        
    def test_of_get_date_and_time(self):
        testDateTime = Transform.Get_Parameter_From_Properties(testdata["features"][0],"observed")
        test_date, test_time = Transform.Convert_To_Date_And_Time(testDateTime)
        self.assertTrue(test_date == "2023-10-26" and test_time == "09:20:00")

"""Unit test of creating a dictionary"""
class test_make_dict(unittest.TestCase):
    testdict = Transform.Make_Dict_From_Data_And_Parameter_List(testdata["features"][0], parameterlist)
    
    def test_dict_len(self):
        self.assertTrue(len(self.testdict) == 7)
        
    def test_dict_longitude(self):
        self.assertEqual(self.testdict["longitude"], 10.4398)

    def test_dict_latitude(self):
        self.assertEqual(self.testdict["latitude"], 55.3088)

    def test_dict_stationId(self):
        self.assertEqual(self.testdict["stationId"], "06126")

    def test_dict_parameter_name(self):
        self.assertEqual(self.testdict["parameterId"], "leav_hum_dur_past10min")

    def test_dict_parameter_value(self):
        self.assertEqual(self.testdict["value"], 0.0)
    
    def test_dict_date(self):
        self.assertEqual(self.testdict["observedDate"], "2023-10-26")

    def test_dict_time(self):
        self.assertEqual(self.testdict["observedTime"], "09:20:00")


"""Unit test of list of dictionaries"""
class test_dictionaries_from_parameters(unittest.TestCase):
    testdict = Transform.Make_Dict_From_Data_And_Parameter_List(testdata["features"][0], parameterlist)
    testlistdict = Transform.Make_Dicts_From_Collection_And_Parameter_List(testdata, parameterlist)
    
    def test_of_list_of_dicts_length(self):
        self.assertEqual(len(self.testlistdict), 3)

    def test_of_dict_length(self):      
        self.assertEqual(len(self.testlistdict[0]), 7)
        
    def test_list_first_entry(self):
        self.assertEqual(self.testdict, self.testlistdict[0])

    def test_of_values(self):
        self.assertEqual(self.testlistdict[0]["stationId"],"06126")
        self.assertEqual(self.testlistdict[0]["parameterId"],"leav_hum_dur_past10min")
        self.assertEqual(self.testlistdict[0]["value"],0.0)
        self.assertEqual(self.testlistdict[0]["observedDate"],"2023-10-26")
        self.assertEqual(self.testlistdict[0]["observedTime"],"09:20:00")
        self.assertEqual(self.testlistdict[0]["longitude"],10.4398)
        self.assertEqual(self.testlistdict[0]["latitude"],55.3088)

    def test_getting_station(self):
        uniqueStations = Transform.Get_Unique_Dict_Items_From_List(self.testlistdict, "stationId")
        self.assertEqual(len(uniqueStations), 2)
        self.assertTrue("06126" in uniqueStations and "06127" in uniqueStations)

class test_dictionaries_from_list_of_collections(unittest.TestCase):
    listOfCollections = [testdata,testdata2]
    testlistdict = Transform.Make_Dicts_From_List_And_Parameter_List(listOfCollections, parameterlist)

    def test_of_list_of_dicts_length(self):
        self.assertEqual(len(self.testlistdict), 4)

class test_empty_features(unittest.TestCase):
    testlistdict = Transform.Make_Dicts_From_Collection_And_Parameter_List(testdata3, parameterlist)
    print(testlistdict)
    def test_dict_lenngth(self):
        self.assertEqual(len(self.testlistdict), 0)

class test_checks(unittest.TestCase):
    parameterListBad = ["properties.badInput", "properties.parameterId",  "properties.value", "properties.observed", "geometry"]

    def test_collection_check(self):
        self.assertTrue(Transform.CollectionCheck(testdata))

    def test_collection_check_fail(self):
        self.assertFalse(Transform.CollectionCheck(testdata["features"][0]))

    def test_feature_check(self):
        self.assertTrue(Transform.FeatureCheck(testdata["features"][0]))

    def test_feature_check_fail(self):
        self.assertFalse(Transform.FeatureCheck(testdata))

    def test_parameter_check(self):
        self.assertTrue(Transform.ParameterCheck(testdata["features"][0],parameterlist))

    def test_parameter_check_fail(self):
        self.assertFalse(Transform.ParameterCheck(testdata,parameterlist))

    def test_parameter_check_fail2(self):
        self.assertFalse(Transform.ParameterCheck(testdata["features"][0],self.parameterListBad))