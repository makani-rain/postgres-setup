
import os
import requests
import json

# URL of the API endpoint
url = "https://streaming-availability.p.rapidapi.com/shows/search/filters"

service = 'paramount'

api_key = os.getenv('RAPID_API_KEY')

# Parameters to send with the GET request
params = {
    "country": 'us',
    "series_granularity": 'show',
    "order_direction": 'desc',
    "order_by": 'original_title',
    "output_language": 'en',
    "catalogs": service,

}

# Headers to send with the GET request
headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "streaming-availability.p.rapidapi.com",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# File to store the JSON responses
output_file = f"data{service}.json"

# Function to make GET requests and handle pagination
def fetch_data(url, params, headers, output_file):
    all_data = []
    has_more = True
    count = 0
    while has_more:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data["shows"])
            
            # Check the pagination flag
            has_more = data["hasMore"]
            
            # Move to the next page
            if has_more and 'nextCursor' in data:
                params["cursor"] = data["nextCursor"]
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            break
        count += 1
        if count > 50:
            input_resp = input("Count is greater than warning limit. Continue? N/n to stop.").lower()
            if input_resp == 'n':
                has_more = False
            count = 0

    # Write all data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(all_data, file, ensure_ascii=False, indent=4)
    
    print(f"Data successfully written to {output_file}")

# Call the function to fetch data
fetch_data(url, params, headers, output_file)

