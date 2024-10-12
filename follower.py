from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

class Follower:
    def __init__(self, id):
        self.id = id
        self.term = 0
        self.logs = []
        self.leader_id = None

    def receive_heartbeat(self, term, leader_id):
        if term >= self.term:
            self.term = term
            self.leader_id = leader_id
            return True
        return False

    def append_entries(self, term, leader_id, entries):
        if term >= self.term:
            self.term = term
            self.leader_id = leader_id
            self.logs = entries
            print(f"Follower {self.id}: Logs actualizados desde el líder {self.leader_id}")
            return True
        return False

    def get_data(self):
        return {"logs": self.logs}

follower = Follower(2)

@app.route('/heartbeat', methods=['POST'])
def handle_heartbeat():
    data = request.json
    success = follower.receive_heartbeat(data['term'], data['leader_id'])
    return jsonify({"success": success})

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.json
    success = follower.append_entries(data['term'], data['leader_id'], data['entries'])
    return jsonify({"success": success})

@app.route('/read_data', methods=['GET'])
def handle_read_request():
    logs = follower.get_data()
    return jsonify(logs)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python follower.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    app.run(port=port)
