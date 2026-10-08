import tkinter as tk
from tkinter import ttk

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

root = tk.Tk()
root.geometry("400x300")

def update_parameters(event):
    selected_api = api_source_choice.get()
    parameter_options = API_parameters.get(selected_api, [])
    parameter_options.sort()
    parameter_choice.delete(0, tk.END)
    parameter_choice.insert(tk.END, *parameter_options)

# Create labels for the input fields
tk.Label(root, text="Choose API").grid(row=0, column=0, padx=10, pady=10)
tk.Label(root, text="Choose Parameter").grid(row=1, column=0, padx=10, pady=10)
tk.Label(root, text="Specify Start Date").grid(row=2, column=0, padx=10, pady=(10,3))
tk.Label(root, text="Specify Start Time\n (FORMAT: HH:MM:SS)").grid(row=3, column=0, padx=10, pady=(3,10))
tk.Label(root, text="Specify End Date").grid(row=4, column=0, padx=10, pady=(10,3))
tk.Label(root, text="Specify End Time\n (FORMAT: HH:MM:SS)").grid(row=5, column=0, padx=10, pady=(3,10))


api_source_choice= ttk.Combobox(root, values=list(API_options.keys()))
api_source_choice.grid(row=0, column=1, padx=10, pady=10)
api_source_choice.bind("<<ComboboxSelected>>", update_parameters)

parameter_choice = tk.Listbox(root, selectmode="multiple", height=0)
parameter_choice.grid(row=1, column=1)

root.mainloop()
