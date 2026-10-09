from dmi_etl.extract import *
from dmi_etl.transform import *
from dmi_etl.DB_operations import *
from dmi_etl.interface import UserInterface

print("testing print")
if __name__ == "__main__":
    print("Hello World")
    ui = UserInterface()
    ui.run()

    all_listOfDicts = []
    all_uniqueStationIds = []
    all_weather_stations = []

    # Go through each package
    for package in ui.request_packages:
        # Unpack the package to get the url and parameters
        url, parameters = ui.get_url_and_params(package)

        extractedData = get_data_with_params(url, parameters)

        parameterlist = ["properties.stationId", "properties.parameterId",  "properties.value", "properties.observed", "geometry"]
        listOfDicts = Make_Dicts_From_Collection_And_Parameter_List(extractedData, parameterlist)
        all_listOfDicts.extend(listOfDicts)

        # Collect supplementary (but also required) data on stations in extracted data
        uniqueStationIds = Get_Unique_Dict_Items_From_List(listOfDicts, "stationId")
        stations_to_request = []
        for id in uniqueStationIds:
            if id not in all_uniqueStationIds:
                stations_to_request.append(id)

        weather_stations = get_station_data(stations_to_request)

        parameterlist_stations = ["properties.stationId",  "properties.name", "geometry"]
        weather_stations = Make_Dicts_From_List_And_Parameter_List(weather_stations,parameterlist_stations)
        # something something, convert the format of weather_stations to the one below for each entry:
        # [{"station_id":"06019", "latitude":55.8766, "longitude": 12.4294}]

        all_weather_stations.extend(weather_stations)

    parameter_info = [{"name":"temp_mean_past1h", "unit":"Celsius", "frequency":"Hourly"},
                      {"name":"humidity_past1h", "unit":"Percent", "frequency":"Hourly"},
                      {"name":"precip_past1h", "unit":"Kilograms per Square Meter", "frequency":"Hourly"},
                      {"name":"wind_speed_past1h", "unit":"Meters per Second", "frequency":"Hourly"}]

    #weather_station = [{"station_id":"06019", "latitude":55.8766, "longitude": 12.4294}]
    #parameter_info = [{"name":"temp_mean_past1h", "unit":"Celsius", "frequency":"Hourly"}]

    #print(listOfDicts)
    engine = get_engine()
    # a raw database connection that allows direct interaction with the database
    connection = engine.raw_connection()
    # the cursor allows us to execute queries and retrieve results from the database
    cursor = connection.cursor()
    create_tables(cursor)

    #first load data into stations, then into parameter and then readings
    load_stations(all_weather_stations, cursor)
    load_parameter(parameter_info, cursor)
    load_readings(all_listOfDicts, cursor)

    connection.commit()
