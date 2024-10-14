from flask import Flask, request, jsonify
import threading
import time
import requests
from flask_cors import CORS 


app = Flask(__name__)
CORS(app)


class Leader:
    def __init__(self):
        self.term = 0
        self.id = 1  # ID del líder
        self.peers = [{"host": "localhost", "port": 5001}, {"host": "localhost", "port": 5002}]  # Lista de followers
        self.store = {}  # Diccionario clave-valor para almacenar los datos

    def send_heartbeats(self):
        while True:
            for peer in self.peers:
                url = f"http://{peer['host']}:{peer['port']}/heartbeat"
                data = {"term": self.term, "leader_id": self.id}
                try:
                    response = requests.post(url, json=data)
                    if response.status_code == 200:
                        print(f"Líder {self.id}: heartbeat enviado correctamente a {peer['port']}")
                    else:
                        print(f"Líder {self.id}: fallo al enviar heartbeat a {peer['port']}")
                except Exception as e:
                    print(f"Líder {self.id}: Error al enviar heartbeat a {peer['port']}: {e}")
            time.sleep(2)

    def append_entries(self, key, value):
        print(f"Líder {self.id} recibió solicitud para almacenar {key}: {value}")
        self.store[key] = value  # Almacenar el par clave-valor
        print(f"Líder {self.id}: Estado actual del almacén: {self.store}")
        
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/append_entries"
            data = {"term": self.term, "leader_id": self.id, "key": key, "value": value}
            try:
                response = requests.post(url, json=data)
                print(f"Respuesta de {peer['port']}: {response.status_code}")
            except Exception as e:
                print(f"Líder {self.id}: Error replicando a {peer['port']}: {e}")
        return {"status": "key-value pair added", "term": self.term}

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.json
    key = data.get("key")
    value = data.get("value")
    print(f"Líder recibió datos: {data}")
    response = leader.append_entries(key, value)
    return jsonify(response)

@app.route('/heartbeat', methods=['POST'])
def handle_heartbeat():
    data = request.json
    print(f"Recibido heartbeat de líder {data.get('leader_id')} en término {data.get('term')}")
    return jsonify({"success": True})

if __name__ == "__main__":
    leader = Leader()  # Crear la instancia de Leader
    threading.Thread(target=leader.send_heartbeats).start()  # Iniciar el envío de heartbeats en un hilo
    print("Líder corriendo en el puerto 5000")
    app.run(port=5000)
