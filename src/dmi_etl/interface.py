import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry

### Dictionaries for API options and parameters ###
API_options = {"DMI readings": "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items",
               "DMI stations": "https://opendataapi.dmi.dk/v2/metObs/collections/station/items",
               "SPAC stations": None}

API_parameters = {"DMI readings": ["temp_mean_past1h", "wind_speed_past1h", "precipitation_past1h"],
                  "DMI stations": ["Sjælsmark", "Jægersborg", 
                                   "Københavns Lufthavn", "Roskilde Lufthavn", "Holbæk Flyveplads", 
                                   "Tessebølle",
                                   "Gedser"],
                  "SPAC readings": [None, None, None, None, None, None],
                  "SPAC stations": ["Ballerup"]}

station_name_to_id = {"Sjælsmark": "06188", 
                      "Jægersborg": "06181", 
                      "Københavns Lufthavn": "06180", 
                      "Roskilde Lufthavn": "06170", 
                      "Holbæk Flyveplads": "06156", 
                      "Tessebølle": "06174", 
                      "Gedser": "06149"}

### Init root window ###

root = tk.Tk()
root.geometry("500x600")

### Functions ###
def update_parameters(event):
    selected_api = api_source_choice.get()
    parameter_options = API_parameters.get(selected_api, [])
    parameter_options.sort()
    parameter_choice.delete(0, tk.END)
    parameter_choice.insert(tk.END, *parameter_options)


def get_selected_timeperiod() -> str:
    start_date_value = start_date.get_date()
    start_time_value = start_time.get()
    if start_time_value == "":
        start_time_value = "00:00:00"
    end_date_value = end_date.get_date()
    end_time_value = end_time.get()
    if end_time_value == "":
        end_time_value = "00:00:00"

    start_datetime = f"{start_date_value}T{start_time_value}Z"
    end_datetime = f"{end_date_value}T{end_time_value}Z"
    #print(f"Selected time period: {start_datetime} to {end_datetime}")
    return "/".join([start_datetime, end_datetime])

# Get all the user input values and return them as a list of request packages
def get_user_input() -> list:
    selected_api = api_source_choice.get()
    chosen_parameters = parameter_choice.curselection()
    time_period = get_selected_timeperiod()
    bbox_entry_value = bbox_entry.get()
    limit_entry_value = limit_entry.get()
    request_packages = [] # create a request package for each selected parameter (since multiple )
    for i in chosen_parameters:
        selected_parameter = parameter_choice.get(i)
        request_package = {"api": selected_api, "api_url": API_options.get(selected_api), 
                           "api_parameters": {"parameterId": selected_parameter, "datetime": time_period, 
                                              "bbox": bbox_entry_value, "limit": limit_entry_value}}
        request_packages.append(request_package)

    return request_packages

# Function to extract URL and parameters from a request package
def get_url_and_params(package) -> tuple:
    api_url = package.get("api_url")
    api_parameters = package.get("api_parameters")
    return api_url, api_parameters
    

### Labels and Input Fields ###

# Create labels for the input fields
tk.Label(root, text="Choose API").grid(row=0, column=0, padx=10, pady=10)
tk.Label(root, text="Choose Parameter").grid(row=1, column=0, padx=10, pady=10)
tk.Label(root, text="Specify Start Date").grid(row=2, column=0, padx=10, pady=(10,3))
tk.Label(root, text="Specify Start Time\n (FORMAT: HH:MM:SS)").grid(row=3, column=0, padx=10, pady=(3,10))
tk.Label(root, text="Specify End Date").grid(row=4, column=0, padx=10, pady=(10,3))
tk.Label(root, text="Specify End Time\n (FORMAT: HH:MM:SS)").grid(row=5, column=0, padx=10, pady=(3,10))
tk.Label(root, text="Set coordinates for bounding box of readings,\n from SE to NW points\n (FORMAT: S,E,N,W)").grid(row=6, column=0, padx=10, pady=(10,3))
tk.Label(root, text="Set limit for number of readings to retrieve").grid(row=7, column=0, padx=10, pady=(10,3))

# "Choose API" dropdown menu
api_source_choice= ttk.Combobox(root, values=list(API_options.keys()))
api_source_choice.grid(row=0, column=1, padx=10, pady=10)
api_source_choice.bind("<<ComboboxSelected>>", update_parameters)

# "Choose Parameter" listbox
parameter_choice = tk.Listbox(root, selectmode="multiple", height=0)
parameter_choice.grid(row=1, column=1)

# Start Date calendar input
start_date = DateEntry(root, width=12, background='green', foreground='white', borderwidth=2)
start_date.grid(row=2, column=1, padx=10, pady=(10,3))

# Start Time entry
start_time = tk.Entry(root)
start_time.grid(row=3, column=1, padx=10, pady=(3,10))

# End Date calendar input
end_date = DateEntry(root, width=12, background='blue', foreground='white', borderwidth=2)
end_date.grid(row=4, column=1, padx=10, pady=(10,3))

# End Time entry
end_time = tk.Entry(root)
end_time.grid(row=5, column=1, padx=10, pady=(3,10))

# Bounding Box entry
bbox_entry = tk.Entry(root)
bbox_entry.grid(row=6, column=1, padx=10, pady=(10,10))

# Limit entry
limit_entry = tk.Entry(root)
limit_entry.grid(row=7, column=1, padx=10, pady=(10,10))

root.mainloop()
