from requests import get
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
location_api_key = os.getenv("LOCATION_API_KEY")


def get_location_api_responce(city_name):
    """Searches for events in the given city"""
    url = "https://concerts-artists-events-tracker.p.rapidapi.com/location"

    current_date = datetime.now().strftime('%Y-%m-%d')
    querystring = {"name": city_name, "minDate": current_date, "maxDate": "2024-12-01", "page": "1"}

    headers = {
        "X-RapidAPI-Key": location_api_key,
        "X-RapidAPI-Host": "concerts-artists-events-tracker.p.rapidapi.com"
    }

    response = get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        try:
            response_json = response.json()
            return response_json
        except ValueError:
            # Handle the case where the response is not valid JSON
            print("Error: Response is not valid JSON.")
            return None
    else:
        # Handle the case where the response status code is not 200
        print(f"Error: Request failed with status code {response.status_code}.")
        return None


def find_artist_location(json_response, artist_name):
    """Searches for events by a specific artist in the previously given city"""
    data = json_response
    for event in data['data']:
        if event['name'] == artist_name:
            location = event['location']['address']
            return {
                'addressLocality': location['addressLocality'],
                'streetAddress': location['streetAddress']
            }
    return False
