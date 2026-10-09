import time
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

### Dictionaries for API options and parameters ###
API_options = {"DMI readings": "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items",
               #"DMI stations": "https://opendataapi.dmi.dk/v2/metObs/collections/station/items",
               "SPAC readings": None
               }

API_parameters = {"DMI readings": ["temp_mean_past1h", "wind_speed_past1h", 
                                   "precip_past1h", "humidity_past1h"],
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

default_values = {"time": "00:00:00", "coordinates": "7,54,16,58", "limit": '100'}

def valid_input(input, expected) -> bool:
    # validate whether the input corresponds to the expected dataformat
    # current options for expected argument: 'time' | 'coordinates' | 'integer'
    if expected == 'time':
        if ":" not in input:
            return False
        segs = input.split(":")
        if len(segs) != 3: # expects three segments (HH, MM, SS)
            return False
        for seg in segs:
            if seg.isnumeric() == False: # each segment must be numeric
                return False
            elif len(seg) != 2: # each segment must be only two characters long
                return False
    elif expected == 'coordinates':
        if "," not in input:
            return False
        segs = input.split(",")
        if len(segs) != 4: # expects four segments (S, E, N, W)
            return False
        for seg in segs:
            if seg.replace(".","").isnumeric() != False: # each segment must be numeric (exluding decimal places)
                return False
    
    elif expected == 'integer':
        if input.isnumeric() == False:
            return False
    
    return True

class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x500")
        self.create_widgets()
        self.halt = 0
        
    def run(self):
            self.root.mainloop()

    def continue_pipeline(self):
        self.halt = 0
        self.root.destroy()

    def exit(self):
        self.halt = 1
        self.root.destroy()
        

    def create_widgets(self):
        # Create labels for the input fields
        tk.Label(self.root, text="Choose API").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Choose parameter").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Specify start date").grid(row=2, column=0, padx=10, pady=(10,3))
        tk.Label(self.root, text="Specify start time\n (FORMAT: HH:MM:SS)").grid(row=3, column=0, padx=10, pady=(3,10))
        tk.Label(self.root, text="Specify end date").grid(row=2, column=2, padx=10, pady=(10,3))
        tk.Label(self.root, text="Specify end time\n (FORMAT: HH:MM:SS)").grid(row=3, column=2, padx=10, pady=(3,10))
        tk.Label(self.root, text="Set coordinates for readings area,\n bound by WS point to EN point\n (FORMAT: W,S,E,N)").grid(row=6, column=0, padx=10, pady=(10,3))
        tk.Label(self.root, text="Set limit\n (Number of readings to retrieve)").grid(row=7, column=0, padx=10, pady=(10,3))

         # "Choose API" dropdown menu
        self.api_source_choice= ttk.Combobox(self.root, values=list(API_options.keys()))
        self.api_source_choice.grid(row=0, column=1, padx=10, pady=10)
        self.api_source_choice.bind("<<ComboboxSelected>>", self.update_parameters)
    
        # "Choose Parameter" listbox
        self.parameter_choice = tk.Listbox(self.root, selectmode="multiple", height=0)
        self.parameter_choice.grid(row=1, column=1)

        #### Calendar inputs ####
        default_start_time = tk.StringVar(self.root, value = default_values["time"])
        default_end_time = tk.StringVar(self.root, value = default_values["time"])

        # Start Date calendar input
        self.start_date = DateEntry(self.root, width=12, background='lightblue', foreground='white', borderwidth=2, date_pattern='dd/mm/y')
        self.start_date.grid(row=2, column=1, padx=10, pady=(12,3))
    
        # Start Time entry
        self.start_time = tk.Entry(self.root, textvariable= default_start_time)
        self.start_time.grid(row=3, column=1, padx=10, pady=(3,12))
    
        # End Date calendar input
        self.end_date = DateEntry(self.root, width=12, background='blue', foreground='white', borderwidth=2, date_pattern='dd/mm/y')
        self.end_date.grid(row=2, column=3, padx=10, pady=(12,3))
    
        # End Time entry
        self.end_time = tk.Entry(self.root, textvariable= default_end_time)
        self.end_time.grid(row=3, column=3, padx=10, pady=(3,12))
    
        # Bounding Box entry
        default_coords = tk.StringVar(self.root, value = default_values["coordinates"])

        self.bbox_entry = tk.Entry(self.root, textvariable = default_coords)
        self.bbox_entry.grid(row=6, column=1, padx=10, pady=(10,10))
    
        # Limit entry
        default_limit = tk.StringVar(self.root, value= default_values['limit'])

        self.limit_entry = tk.Entry(self.root, textvariable= default_limit)
        self.limit_entry.grid(row=7, column=1, padx=10, pady=(10,10))
    
        # Submit and continue button
        continue_button = tk.Button(self.root, text="Submit request\n and continue", command=self.submit_and_continue)
        continue_button.grid(row=8, column=2, columnspan=1, pady=20, ipadx = 30)

        # Exit button
        exit_button = tk.Button(self.root, text="Exit", command=self.exit)
        exit_button.grid(row=8, column=3, columnspan=1, pady=10, ipadx = 30, ipady=8)

    def display_error(self, msg):
        pass
    
    ### Functions ###
    def update_parameters(self, event):
        selected_api = self.api_source_choice.get()
        parameter_options = API_parameters.get(selected_api, [])
        parameter_options.sort()
        self.parameter_choice.delete(0, tk.END)
        self.parameter_choice.insert(tk.END, *parameter_options)


    def get_selected_timeperiod(self) -> str:
        start_date_value = self.start_date.get_date()
        start_time_value = self.start_time.get()
        if start_time_value == "":
            start_time_value = "00:00:00"
        end_date_value = self.end_date.get_date()
        end_time_value = self.end_time.get()
        if end_time_value == "":
            end_time_value = "00:00:00"

        if valid_input(start_time_value, 'time') and valid_input(end_time_value, 'time'):
            start_datetime = f"{start_date_value}T{start_time_value}Z"
            end_datetime = f"{end_date_value}T{end_time_value}Z"
            #print(f"Selected time period: {start_datetime} to {end_datetime}")
            return "/".join([start_datetime, end_datetime])
        else:
            self.display_error("One or more inputs are invalid: Time value(s) does not adhere to format.")
            return ""

    # Get all the user input values and return them as a list of request packages
    def get_user_input(self):
        selected_api = self.api_source_choice.get()
        chosen_parameters = self.parameter_choice.curselection()
        time_period = self.get_selected_timeperiod()
        bbox_entry_value = self.bbox_entry.get()
        limit_entry_value = self.limit_entry.get()
        request_packages = [] # create a request package for each selected parameter (since multiple parameterIds will otherwise conflict with the API)
        for i in chosen_parameters:
            selected_parameter = self.parameter_choice.get(i)
            request_package = {"api": selected_api, "api_url": API_options.get(selected_api), 
                            "api_parameters": {"parameterId": selected_parameter, "datetime": time_period, 
                                                "bbox": bbox_entry_value, "limit": limit_entry_value}}
            request_packages.append(request_package)

        self.request_packages = request_packages

    # store the request and exit the interface
    def submit_and_continue(self):
        self.get_user_input()
        self.continue_pipeline()

    # Function to extract URL and parameters from a request package
    def get_url_and_params(self,package) -> tuple:
        api_url = package.get("api_url")
        api_parameters = package.get("api_parameters")
        return api_url, api_parameters

if __name__ == "__main__":
    ui = UserInterface()
    time.sleep(0.5)
    ui.run()
    print(f"Constructed packages: {getattr(ui, "request_packages", [])}")
    
    
    
        


