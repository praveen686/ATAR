import json

import pandas as pd
import requests

base_url = "http://localhost:8000"

# POST request to /post/instruments
post_endpoint = "/post/instruments"
post_params = {
    "instrument_ids": "AUDUSD",
    "use_literal_ids": False
}
post_response = requests.post(base_url + post_endpoint, params=post_params)
post_data = post_response.json()

# Extract the relevant data from the JSON response
post_data = post_data.get("data")

print(f'{post_data = }')

# GET request to /get/quotes
get_endpoint = "/get/quotes"
get_params = {
    "instrument_ids": "AUDUSD",
    "start_date": "2021-01-04",
    "end_date": "2021-01-05",
    "use_literal_ids": False
}
get_headers = {
    "Content-Type": "application/json"
}
get_response = requests.get(base_url + get_endpoint, json=get_params, headers=get_headers)
get_data = get_response.json()

# Print the raw JSON data
print(json.dumps(get_data, indent=4))

# Only try to convert to DataFrame if there is data
if get_data.get('data') is not None:
    get_df = pd.read_json(get_data['data'], orient='split')
    print(get_df)
else:
    print("No data received.")

