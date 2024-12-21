import requests
import time
import json
from pathlib import Path

# Constants
API_URL = 'https://api.semanticscholar.org/graph/v1/paper/batch'
HEADERS = {}  # Add API key if needed, e.g., {"x-api-key": "your_api_key"}
PAYLOAD = {
    "ids": ["https://arxiv.org/abs/2404.00282v3", "https://arxiv.org/abs/2404.18638"]
}
PARAMS = {
    'fields': 'title,publicationDate,abstract,citationCount,venue,publicationVenue.type,influentialCitationCount,authors.name,authors.affiliation,openAccessPdf.url'
}
MAX_RETRIES = 5  # Maximum number of retries
BACKOFF_FACTOR = 2  # Exponential backoff factor
OUTPUT_FILE = Path("response_data.json")

def fetch_data_with_retries(api_url, headers, params, payload, max_retries, backoff_factor):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(api_url, headers=headers, params=params, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request failed with status code {response.status_code}: {response.text}")
                # Retry only on server errors (5xx) or rate-limiting (429)
                if response.status_code in [429] or (500 <= response.status_code < 600):
                    raise requests.exceptions.RequestException("Server-side error or rate-limiting.")
                else:
                    break  # Non-retryable error
        except requests.exceptions.RequestException as e:
            retries += 1
            wait_time = backoff_factor ** retries
            print(f"Retry {retries}/{max_retries} after {wait_time}s due to: {e}")
            time.sleep(wait_time)
    return None

def save_to_json_file(data, output_file):
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Failed to save data to file: {e}")

# Main
if __name__ == "__main__":
    response_data = fetch_data_with_retries(API_URL, HEADERS, PARAMS, PAYLOAD, MAX_RETRIES, BACKOFF_FACTOR)
    if response_data:
        save_to_json_file(response_data, OUTPUT_FILE)
    else:
        print("Failed to fetch data after multiple retries.")