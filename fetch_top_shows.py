
import os
import requests
import json

url = "https://streaming-availability.p.rapidapi.com/shows/top"

api_key = os.getenv('RAPID_API_KEY')

services = ['netflix',
            'prime',
            'disney',
            'apple',
            'hbo']


headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "streaming-availability.p.rapidapi.com",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def fetch_data(url, headers):
    for service in services:
        params = {
            "country": 'us',
            "service": service,
        }
    
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()

            output_file = f"top{service}.json"
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            print(f"Failed to retrieve data for {service}: {response.status_code}")
            break
    
        
        print(f"Data successfully written to {output_file}")

fetch_data(url, headers)

