from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

class Follower:
    def __init__(self, id):
        self.id = id
        self.term = 0
        self.store = {}  # Diccionario clave-valor para almacenar los datos replicados

    def append_entries(self, key, value):
        # Almacenar la clave-valor replicada por el líder
        self.store[key] = value
        print(f"Follower {self.id}: Clave-valor replicada {key}: {value}")
        return True

    def get_data(self, key):
        # Devolver el valor asociado a la clave si existe
        return {"key": key, "value": self.store.get(key, "Clave no encontrada")}

follower = None  # Variable global para la instancia del follower

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.json
    key = data.get("key")
    value = data.get("value")
    success = follower.append_entries(key, value)
    return jsonify({"success": success})

@app.route('/read_data', methods=['GET'])
def handle_read_request():
    key = request.args.get("key")
    response = follower.get_data(key)
    return jsonify(response)

@app.route('/heartbeat', methods=['POST'])
def handle_heartbeat():
    data = request.json
    print(f"Follower {follower.id} recibió heartbeat de líder {data.get('leader_id')} en término {data.get('term')}")
    return jsonify({"success": True})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python follower.py <puerto>")
        sys.exit(1)

    port = int(sys.argv[1])
    follower = Follower(port)  # Crear una instancia del follower con el puerto como ID
    print(f"Follower {follower.id} corriendo en el puerto {port}")
    app.run(port=port)
