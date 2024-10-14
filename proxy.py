from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

class Proxy:
    def __init__(self, leader_host, leader_port, followers):
        self.leader_url = f"http://{leader_host}:{leader_port}/append_entries"
        self.followers = followers

    def forward_write_request(self, key, value):
        data = {"key": key, "value": value}
        print(f"Enviando solicitud de escritura al líder con data: {data}")
        try:
            # Aquí usamos requests directamente para enviar el POST al líder
            response = requests.post(self.leader_url, json=data)
            if response.status_code == 200:
                print(f"Respuesta del líder: {response.json()}")
                return response.json()
            else:
                print(f"Error al comunicarse con el líder. Código de estado: {response.status_code}")
                return {"error": f"Error al comunicarse con el líder: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            print(f"Excepción al intentar comunicarse con el líder: {e}")
            return {"error": f"Error al comunicarse con el líder: {str(e)}"}

    def forward_read_request(self, key):
        follower = random.choice(self.followers)
        url = f"http://{follower['host']}:{follower['port']}/read_data"
        print(f"Enviando solicitud de lectura a {url} con clave: {key}")
        try:
            response = requests.get(url, params={"key": key})
            if response.status_code == 200:
                print(f"Respuesta del follower: {response.json()}")
                return response.json()
            else:
                print(f"Error al comunicarse con el follower. Código de estado: {response.status_code}")
                return {"error": f"Error al comunicarse con el follower: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            print(f"Excepción al intentar comunicarse con el follower: {e}")
            return {"error": f"Error al comunicarse con el follower: {str(e)}"}

proxy = Proxy("localhost", 5005, [{"host": "localhost", "port": 5001}, {"host": "localhost", "port": 5002}])

@app.route('/client_write', methods=['POST'])
def handle_write_request():
    data = request.json
    key = data.get("key")
    value = data.get("value")
    response = proxy.forward_write_request(key, value)
    return jsonify(response)

@app.route('/client_read', methods=['GET'])
def handle_read_request():
    key = request.args.get("key")
    response = proxy.forward_read_request(key)
    return jsonify(response)

if __name__ == "__main__":
    print("Proxy corriendo en el puerto 5003")
    app.run(port=5003)
