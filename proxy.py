from flask import Flask, request, jsonify
from common import send_post_request, send_get_request
import random

app = Flask(__name__)

class Proxy:
    def __init__(self, leader_host, leader_port, followers):
        self.leader_url = f"http://{leader_host}:{leader_port}/append_entries"
        self.followers = followers

    def forward_write_request(self, command):
        data = {"command": command}
        return send_post_request(self.leader_url, data)

    def forward_read_request(self):
        follower = random.choice(self.followers)
        url = f"http://{follower['host']}:{follower['port']}/read_data"
        return send_get_request(url)

proxy = Proxy("localhost", 5000, [{"host": "localhost", "port": 5001}, {"host": "localhost", "port": 5002}])

@app.route('/client_write', methods=['POST'])
def handle_write_request():
    data = request.json
    command = data.get("command")
    response = proxy.forward_write_request(command)
    return jsonify(response)

@app.route('/client_read', methods=['GET'])
def handle_read_request():
    response = proxy.forward_read_request()
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5003)
