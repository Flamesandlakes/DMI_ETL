import requests

# testfunction inspired by article to extract data from the API


# function to extract data from the API
def get_data(url):
    response = requests.get(url)
    data = response.json()
    
    return data

def get_data_with_params(base_url: str, parameters: dict):
    response = requests.get(url = base_url, params = parameters)
    data = response.json()
    return data

def get_station_data(station_list):
    data_list = []
    base_url = "https://opendataapi.dmi.dk/v2/metObs/collections/station/items?"
    for station in station_list:
        response = requests.get(url = base_url + "stationId=" + station)
        data = response.json()
        data_list.append(data)
    return data_list


if __name__ == "__main__":
    DMI_url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items?datetime=2018-02-12T00:00:00Z/2018-03-18T12:31:12Z&limit=100&offset=1000&bbox=7,54,16,58"

    DMI_base_url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"
    # afprøvning af testfunktion
    parameters = {"datetime": "2018-02-12T00:00:00Z/2018-03-18T12:31:12Z", 
                "limit": 10, "offset": 0, "bbox": "7,54,16,58", "parameterId": ["temp_mean_past1h"]}#, "humidity_past1h"]}

    #print(get_data(DMI_url))
    #print(get_data_with_params(DMI_base_url, parameters))

    parameters["datetime"] = "2026-10-02T00:00:00Z/2026-10-02T12:00:00Z"
    parameters["offset"] = 0
    parameters["stationId"] = "06188" # Sjælsmark
    parameters.pop("bbox")

    print(get_data_with_params(DMI_base_url, parameters))
    #print(parameters)
    #parameters
