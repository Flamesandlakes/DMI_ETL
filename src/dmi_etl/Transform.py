import datetime

"""
to do:
    - timeresoution
    - units
"""


"""Gets the geolocation of station"""
def Get_Location(data):
    geo = data["features"][0]["geometry"]["coordinates"]
    return geo


"""Returns the property dictionary from the data"""
def Get_Properties(data):
    return data["features"][0]["properties"]


"""Returns the stationId of the data"""
def Get_StationId(data):
    PropertiesOfData = Get_Properties(data)
    return PropertiesOfData["stationId"]


"""Returns the parameter name and value in the data if it exists"""
def Get_Parameter(data):
    PropertiesOfData = Get_Properties(data)
    if "parameterId" in PropertiesOfData:
        return PropertiesOfData["parameterId"], PropertiesOfData["value"]
    else:
        return None, None


"""Returns two strings with the date and time the data was taken"""
def Get_Date_And_Time(data):
    TimeStampString = data["timeStamp"]
    Date_obj = datetime.datetime.strptime(TimeStampString, "%Y-%m-%dT%H:%M:%SZ")
    Date = Date_obj.strftime("%Y-%m-%d")
    Time = Date_obj.strftime("%H:%M:%S")
    return Date, Time


"""Makes a dictionary of key elements of the given data"""
def Make_Dict_From_Data(data):
    DMI_Dictionary = {}
    Longitude, Latitude = Get_Location(data)
    DMI_Dictionary.update({"Longitude": Longitude, "Latitude" : Latitude})
    
    DMI_Dictionary.update({"stationId": Get_StationId(data)})

    Parameter_Name, Parameter_Value = Get_Parameter(data)
    DMI_Dictionary.update({"ParameterName": Parameter_Name, "ParameterValue": Parameter_Value})

    Date, Time = Get_Date_And_Time(data)
    DMI_Dictionary.update({"Date": Date, "Time": Time})
    return DMI_Dictionary


"""Makes a list of dictionaries from a given list of data"""
def Make_Dicts_From_List(datalist):
    List_Of_Dicts = []
    for datadict in datalist:
        New_Dict = Make_Dict_From_Data(datadict)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts