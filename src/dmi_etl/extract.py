import requests

# testfunction inspired by article to extract data from the API
# fjernes når den rigtige funktion virker på DMI's api
def test_get_data():
    url = "https://official-joke-api.appspot.com/random_ten"
    response = requests.get(url)
    data = response.json()

    return data

# function to extract data from the API
def get_data():
    url = "?"
    response = requests.get(url)
    data = response.json()
    
    return data

# afprøvning af testfunktion
print(test_get_data())