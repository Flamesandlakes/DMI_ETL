import datetime
import re

"""
to do:
    - timeresoution
    - units
    - names
"""

timeFormat = re.compile('.*-.*-.*:.*:.*')

nodeId_to_location = {"ae6901bb-6703-4955-9d59-179c1ee5dae8":{"stationId": "ae6901bb-6703-4955-9d59-179c1ee5dae8", "name": "Ballerup Akademi", "longitude": 12.3876, "latitude": 55.7357},
        "2c47284d-777b-44f0-bdeb-3d442f6a31b1":{"stationId": "2c47284d-777b-44f0-bdeb-3d442f6a31b1", "name": "Odense Akademi", "longitude": 10.2112 , "latitude": 56.1554},
        "6d437168-7432-470b-9cf4-08439d0127ad":{"stationId": "6d437168-7432-470b-9cf4-08439d0127ad", "name": "Aarhus Akademi", "longitude": 10.3880 , "latitude": 55.4025},
        "NOT_RECOGNIZED":{"stationId": "NOT_RECOGNIZED", "name": "TBD", "longitude": None , "latitude": None}
    }

"""Gets the geolocation of station as longitude, latitude"""
def Get_Location(data):
    geo = data["geometry"]["coordinates"]
    return geo


"""Gets the specified parameter from the property of a given data entry"""
def Get_Parameter_From_Properties(data,parameter_name):
    return data["properties"][parameter_name]


"""Converts the datetime string into seperate date and time"""
def Convert_To_Date_And_Time(datetime_string):
    datetime_string = Normalize_Datetime(datetime_string)
    Date_obj = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ")
    Date = Date_obj.strftime("%Y-%m-%d")
    Time = Date_obj.strftime("%H:%M:%S")
    return Date, Time


"""Returns all unique entries of a key from a list of dictionaries"""
def Get_Unique_Dict_Items_From_List(dictlist, key):
    itemlist = []
    for dictionary in dictlist:
        item = dictionary[key]
        itemlist.append(item)
    return list(set(itemlist))


"""Makes a dictionary based on the given data and list of parameters"""
def Make_Dict_From_Data_And_Parameter_List(data, parameter_list):
    Dictionary = {}
    for parameter in parameter_list:
        if parameter.startswith("properties."):
            parameter = parameter.removeprefix("properties.")
            parameter_value = Get_Parameter_From_Properties(data,parameter)

            if timeFormat.match(str(parameter_value)) is not None:
                parameter_date, parameter_time = Convert_To_Date_And_Time(parameter_value)
                Dictionary.update({parameter+"Date": parameter_date, parameter+"Time": parameter_time})
            else:
                Dictionary.update({parameter: parameter_value})
                
        elif parameter == "geometry":
            Longitude, Latitude = Get_Location(data)
            Dictionary.update({"longitude": Longitude, "latitude" : Latitude})
        else:
            Dictionary.update({parameter: parameter_value})
    return Dictionary


"""Makes a list of dictionaries from a collection and a list of parameters"""
def Make_Dicts_From_Collection_And_Parameter_List(Collection, parameter_list):
    List_Of_Dicts = []
    for datadict in Collection["features"]:
        New_Dict = Make_Dict_From_Data_And_Parameter_List(datadict, parameter_list)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts


"""Makes a list of dictionaries from a list of collections and a list of parameters"""
def Make_Dicts_From_List_And_Parameter_List(collection_list, parameter_list): 
    List_Of_Dicts = []
    for collection in collection_list:
        New_Dict_List = Make_Dicts_From_Collection_And_Parameter_List(collection, parameter_list)
        List_Of_Dicts.extend(New_Dict_List)
    return List_Of_Dicts


"""Checks collection for containing features"""
def CollectionCheck(collection):
    if collection["type"] == "FeatureCollection" and "features" in collection:
        return True
    else:
        return False


"""Checks feature for geometry and properties"""
def FeatureCheck(feature):
    if feature ["type"] == "Feature" and"geometry" in feature and "properties" in feature:
        return True
    else:
        return False
    

"""Checks a feature for containing the expected parameters"""
def ParameterCheck(feature, parameterlist):
    allValid = True
    for parameter in parameterlist:
        location = parameter.split(".")
        if len(location) == 1:
            if location[0] not in feature:
                allValid = False
                break
        else:
            if location[0] in feature:
                if location[1] not in feature[location[0]]:
                    allValid = False
                    break
            else:
                allValid = False
                break
    return allValid


"""Normalize all datetime.datetime timestamps to second precision (dop milliseconds)"""
def Normalize_Datetime(datetime_string: str):
    # to seconds (ie. drop milliseconds)
    string =  datetime_string.split(".")[0]
    if string.endswith("Z"):
        return string
    else:
        return string + "Z"

def Format_Value(value):
    return round(value, 2)

"""Take a SPAC obervation and make its naming scheme compatible with the existing pipeline"""
def Reformat_SPAC_Observation(observation: dict):
    Date, Time = Convert_To_Date_And_Time(observation["timestamp"])
    reformated_dict = {"stationId": Map_NodeId_to_Location_as_entry(observation["nodeId"]),
                       "parameterId": observation["sensor"] if observation["instrumentModel"] != "DS18B20" else "temperature",
                       "value": Format_Value(observation["value"]),
                       "observedDate": Date,
                       "observedTime": Time,
                       "longitude": None,
                       "latitude": None}
    return reformated_dict

def Make_Dicts_From_Observations(observations_dict: dict):
    listOfObs = [Reformat_SPAC_Observation(obs) for obs in observations_dict["observations"]]
    return listOfObs

def Map_NodeId_to_Location_as_station(nodeId):
    if nodeId in nodeId_to_location:
        return nodeId_to_location[nodeId]
    else:
        return nodeId_to_location["NOT_RECOGNIZED"]

def Map_NodeId_to_Location_as_entry(nodeId):
    if nodeId in nodeId_to_location:
        return nodeId
    else:
        return "NOT_RECOGNIZED"