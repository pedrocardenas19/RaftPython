import requests
import json

def send_post_request(url, data):
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending POST request to {url}: {e}")
        return None

def send_get_request(url):
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Error sending GET request to {url}: {e}")
        return None
