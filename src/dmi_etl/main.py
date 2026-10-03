from dmi_etl.extract import *
from dmi_etl.transform import *
from dmi_etl.DB_operations import *

DMI_base_url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

parameters = {"datetime": "2018-02-12T00:00:00Z/2018-03-18T12:31:12Z", 
                "limit": 10, "offset": 0, "bbox": "7,54,16,58", "parameterId": ["temp_mean_past1h"]}

extractedData = get_data_with_params(DMI_base_url, parameters)

listOfDicts = Make_Dicts_From_Collection(extractedData)

if __name__ == "__main__":
    print(listOfDicts)