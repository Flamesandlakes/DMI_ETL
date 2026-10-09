import requests
import time

class RateConstraint():
    # DMI_ratelimit is 500 requests per 5 seconds, = 0.6 sec per request 
    def __init__(self, ratelimit = 500, time_to_exceed = 5):
        self.ratelimit = ratelimit
        self.time_to_exceed = time_to_exceed
        self.calls_so_far = 0
        self.reference_time = time.time()

    def reset_call_count(self):
        self.calls_so_far = 0

    def count_call(self):
        self.calls_so_far += 1
        if self.calls_so_far >= self.ratelimit:
            if (time.time() - self.reference_time) >= self.time_to_exceed:
                time.sleep(self.time_to_exceed)
                self.reset_call_count()
                self.reference_time = time.time()


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
    ratefollower = RateConstraint()
    for station in station_list:
        response = requests.get(url = base_url + "stationId=" + station)
        data = response.json()
        data_list.append(data)
        ratefollower.count_call()
        
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
