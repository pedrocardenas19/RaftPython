import requests
import json

# Enviar una petición POST a otro nodo
def send_post_request(url, data):
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error en la solicitud POST a {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al intentar hacer POST a {url}: {e}")
        return None

# Enviar una petición GET
def send_get_request(url):
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Error sending GET request to {url}: {e}")
        return None
