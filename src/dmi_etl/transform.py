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


"""makes a dictionary based on the given data and list of parameters"""
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


def Make_Dicts_From_Collection_And_Parameter_List(Collection, parameter_list):
    List_Of_Dicts = []
    for datadict in Collection["features"]:
        New_Dict = Make_Dict_From_Data_And_Parameter_List(datadict, parameter_list)
        List_Of_Dicts.append(New_Dict)
    return List_Of_Dicts

def Make_Dicts_From_List_And_Parameter_List(collection_list, parameter_list): 
    List_Of_Dicts = []
    for collection in collection_list:
        New_Dict_List = Make_Dicts_From_Collection_And_Parameter_List(collection, parameter_list)
        List_Of_Dicts.extend(New_Dict_List)
    return List_Of_Dicts




#check for features, properties, geometry
def CollectionCheck(collection):
    if collection["type"] == "FeatureCollection" and "features" in collection:
        return True
    else:
        return False

def FeatureCheck(feature):
    if feature ["type"] == "Feature" and"geometry" in feature and "properties" in feature:
        return True
    else:
        return False
    

    
#check for parameters
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