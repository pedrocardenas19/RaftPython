from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

class Follower:
    def __init__(self, id):
        self.id = id
        self.store = {}  # Diccionario para almacenar datos replicados

    def append_entries(self, key, value):
        # Almacenar el par clave-valor replicado
        self.store[key] = value
        print(f"Follower {self.id}: Clave-valor replicada {key}: {value}")
        return True

    def print_store(self):
        while True:
            print(f"Follower {self.id} - Almacén actual: {self.store}")
            time.sleep(10)  # Imprime cada 10 segundos

follower = None

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
    if key in follower.store:
        return jsonify({"key": key, "value": follower.store[key]})
    else:
        return jsonify({"error": "Clave no encontrada"}), 404

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python follower.py <puerto>")
        sys.exit(1)

    port = int(sys.argv[1])
    follower = Follower(port)
    
    # Iniciar el hilo de impresión
    threading.Thread(target=follower.print_store, daemon=True).start()

    print(f"Follower {follower.id} corriendo en el puerto {port}")
    app.run(port=port)
