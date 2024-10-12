from flask import Flask, request, jsonify
from common import send_post_request
import threading
import time

app = Flask(__name__)

class Leader:
    def __init__(self):
        self.term = 0
        self.id = 1  # ID del líder
        self.peers = [{"host": "localhost", "port": 5001}, {"host": "localhost", "port": 5002}]  # Lista de followers
        self.logs = []

    def send_heartbeats(self):
        while True:
            for peer in self.peers:
                url = f"http://{peer['host']}:{peer['port']}/heartbeat"
                data = {"term": self.term, "leader_id": self.id}
                try:
                    response = send_post_request(url, data)
                    if response and response.get("success"):
                        print(f"Líder {self.id}: heartbeat enviado correctamente a {peer['port']}")
                    else:
                        print(f"Líder {self.id}: fallo al enviar heartbeat a {peer['port']}")
                except Exception as e:
                    print(f"Líder {self.id}: Error al enviar heartbeat a {peer['port']}: {e}")
            time.sleep(2)

    def append_entries(self, command):
        self.logs.append({"command": command, "term": self.term})
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/append_entries"
            data = {"term": self.term, "leader_id": self.id, "entries": self.logs}
            try:
                send_post_request(url, data)
                print(f"Líder {self.id}: Entrada de log replicada en {peer['port']}")
            except Exception as e:
                print(f"Líder {self.id}: Error al replicar log en {peer['port']}: {e}")

leader = Leader()

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.json
    command = data.get("command")
    leader.append_entries(command)
    return jsonify({"status": "log added", "term": leader.term})

@app.route('/heartbeat', methods=['POST'])
def handle_heartbeat():
    data = request.json
    print(f"Recibido heartbeat de líder {data.get('leader_id')} en término {data.get('term')}")
    return jsonify({"success": True})

if __name__ == "__main__":
    threading.Thread(target=leader.send_heartbeats).start()
    app.run(port=5000)
