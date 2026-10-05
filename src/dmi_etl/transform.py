import datetime
import re

"""
to do:
    - timeresoution
    - units
    - names
"""

timeFormat = re.compile('.*-.*-.*:.*:.*')

"""Gets the geolocation of station as longitude, latitude"""
def Get_Location(data):
    geo = data["geometry"]["coordinates"]
    return geo


"""Returns the property dictionary from the data"""
def Get_Properties(data):
    return data["properties"]


"""Returns the stationId of the data"""
def Get_StationId(properties):
    return properties["stationId"]


"""Returns the parameter name and value in the data if it exists"""
def Get_Parameter(properties):
    if "parameterId" in properties:
        return properties["parameterId"], properties["value"]
    else:
        return None, None


"""Returns two strings with the date and time the data was taken"""
def Get_Date_And_Time(data,parameter_name):
    TimeObservedString = data["properties"]["parameter_name"]
    Date_obj = datetime.datetime.strptime(TimeObservedString, "%Y-%m-%dT%H:%M:%SZ")
    Date = Date_obj.strftime("%Y-%m-%d")
    Time = Date_obj.strftime("%H:%M:%S")
    return Date, Time


"""Makes a dictionary of key elements of the given data"""
def Make_Dict_From_Data(data):
    DMI_Dictionary = {}
    Longitude, Latitude = Get_Location(data)
    DMI_Dictionary.update({"Longitude": Longitude, "Latitude" : Latitude})

    PropertiesOfData = Get_Properties(data)

    DMI_Dictionary.update({"stationId": Get_StationId(PropertiesOfData)})

    Parameter_Name, Parameter_Value = Get_Parameter(PropertiesOfData)
    DMI_Dictionary.update({"ParameterName": Parameter_Name, "ParameterValue": Parameter_Value})

    Date, Time = Get_Date_And_Time(data, "observed")
    DMI_Dictionary.update({"Date": Date, "Time": Time})
    return DMI_Dictionary


"""Makes a list of dictionaries from a given data collection"""
def Make_Dicts_From_Collection(Collection):
    List_Of_Dicts = []
    for datadict in Collection["features"]:
        New_Dict = Make_Dict_From_Data(datadict)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts


"""gets the specified parameter from the property of a given data entry"""
def Get_Parameter_From_Properties(data,parameter_name):
    return data["properties"][parameter_name]


"""Converts the datetime string into seperate date and time"""
def Convert_To_Date_And_Time(datetime_string):
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


"""returns a dictionary for the given station data"""
def Make_Dict_From_Station_Data(data):
    DMI_Dictionary = {}
    Longitude, Latitude = Get_Location(data)
    DMI_Dictionary.update({"Longitude": Longitude, "Latitude" : Latitude})

    DMI_Dictionary.update({"stationId": Get_Parameter_From_Properties(data, "stationId")})
    DMI_Dictionary.update({"name": Get_Parameter_From_Properties(data, "name")})

    Date, Time = Get_Date_And_Time(data, "operationFrom")
    DMI_Dictionary.update({"Date": Date, "Time": Time})
    return DMI_Dictionary


"""makes a list of dictionaries from the given station collection"""
def Make_Dicts_From_Station_Collection(Collection):
    List_Of_Dicts = []
    for datadict in Collection["features"]:
        New_Dict = Make_Dict_From_Station_Data(datadict)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts


"""makes a dictionary based on the given data and list of parameters"""
def Make_Dict_From_Data_And_Parameter_List(data, parameter_list):
    Dictionary = {}
    for parameter in parameter_list:
        if parameter.startswith("properties."):
            parameter = parameter.removeprefix("properties.")
            parameter_value = Get_Parameter_From_Properties(data,parameter)
            if isinstance(parameter_value, str):
                if timeFormat.match(parameter_value) is not None:
                    parameter_date, parameter_time = Convert_To_Date_And_Time(parameter_value)
                    Dictionary.update({parameter+"Date": parameter_date, parameter+"Time": parameter_time})
                else:
                    Dictionary.update({parameter: parameter_value})
        elif parameter == "geometry":
            Longitude, Latitude = Get_Location(data)
            Dictionary.update({"longitude": Longitude, "latitude" : Latitude})
    return Dictionary


def Make_Dicts_From_Collection_And_Parameter_List(Collection, parameter_list):
    List_Of_Dicts = []
    for datadict in Collection["features"]:
        New_Dict = Make_Dict_From_Data_And_Parameter_List(datadict, parameter_list)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts

def Make_Dicts_From_List_And_Parameter_List(station_list, parameter_list): 
    List_Of_Dicts = []
    for station in station_list:
        New_Dict_List = Make_Dicts_From_Collection_And_Parameter_List(station, parameter_list)
        List_Of_Dicts.extend(New_Dict_List)
    return List_Of_Dicts
