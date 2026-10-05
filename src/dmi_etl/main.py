from dmi_etl.extract import *
from dmi_etl.transform import *
from dmi_etl.DB_operations import *

DMI_base_url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

parameters = {"datetime": "2018-02-12T00:00:00Z/2018-03-18T12:31:12Z", 
                "limit": 10, "offset": 0, "bbox": "7,54,16,58", "parameterId": ["temp_mean_past1h"]}

extractedData = get_data_with_params(DMI_base_url, parameters)


parameterlist = ["properties.stationId", "properties.parameterId",  "properties.value", "properties.observed", "geometry"]
listOfDicts = Make_Dicts_From_Collection_And_Parameter_List(extractedData,parameterlist)
stationList = Get_Unique_Dict_Items_From_List(listOfDicts, "stationId")

stationData = get_station_data(stationList)

stationParameters = ["properties.stationId", "properties.parameterId",  "properties.name", "properties.operationFrom", "geometry"]
stationDicts = Make_Dicts_From_List_And_Parameter_List(stationData, stationParameters)


weather_station = [{"station_id":"06019", "latitude":55.8766, "longitude": 12.4294}]
parameter_info = [{"name":"temp_mean_past1h", "unit":"Celsius", "frequency":"Hourly"}]

engine = get_engine()
# a raw database connection that allows direct interaction with the database
connection = engine.raw_connection()
# the cursor allows us to execute queries and retrieve results from the database
cursor = connection.cursor()
create_tables(cursor)

#first load data into stations, then into parameter and then readings
load_stations(weather_station, cursor)
load_parameter(parameter_info, cursor)
load_readings(listOfDicts, cursor)

connection.commit()



if __name__ == "__main__":
    print(listOfDicts)
    print(stationList)
    print(stationDicts)