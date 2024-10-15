from flask import Flask, request, jsonify
import threading
import time
import random
import sys
import logging
import requests  # Asegúrate de importar requests si no está ya en tu código

app = Flask(__name__)

# Configurar el logger para registrar solo errores en un archivo
logger = logging.getLogger('raft_node')
logger.setLevel(logging.ERROR)

# Crear un manejador de archivo que registre los errores
fh = logging.FileHandler('raft_node_errors.txt')
fh.setLevel(logging.ERROR)

# Crear un formateador y añadirlo al manejador
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# Añadir el manejador al logger
logger.addHandler(fh)

class RaftNode:
    def __init__(self, id, port, peers):
        self.id = id
        self.port = port
        self.peers = peers  # Lista de otros nodos
        self.term = 0
        self.logs = {}
        self.leader_id = None
        self.voted_for = None
        self.state = "follower"  # El estado inicial es 'follower'
        self.election_timeout = random.uniform(5, 10)  # Timeout aleatorio
        self.vote_count = 0

        # Iniciar el thread para imprimir el estado periódicamente
        self.state_printer_thread = threading.Thread(target=self.print_state_periodically)
        self.state_printer_thread.daemon = True  # Permite que el thread se cierre con el programa
        self.state_printer_thread.start()

        # Iniciar el temporizador de la elección
        self.timer = threading.Timer(self.election_timeout, self.start_election)
        self.timer.start()

    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.election_timeout, self.start_election)
        self.timer.start()

    def receive_heartbeat(self, term, leader_id, leader_logs):
      if term >= self.term:
          self.state = "follower"
          self.term = term
          self.leader_id = leader_id
          self.voted_for = None
          self.reset_timer()
          print(f"Follower {self.id}: Heartbeat recibido correctamente del líder {leader_id}.")

          # Sincronizar logs
          if self.logs != leader_logs:
              print(f"Follower {self.id}: Actualizando logs para sincronizar con el líder {leader_id}.")
              self.logs = leader_logs.copy()
          return True
      return False

    def append_entries(self, term, leader_id, key, value):
      if term >= self.term:
          self.term = term
          self.leader_id = leader_id
          self.logs[key] = value
          self.reset_timer()
          print(f"Nodo {self.id}: Logs actualizados desde el líder {self.leader_id}. Clave: {key}, Valor: {value}")
          return True
      else:
          print(f"Nodo {self.id}: No se pudieron actualizar los logs desde el líder {leader_id}. Término incorrecto.")
          print(f"Término recibido: {term}, Término actual: {self.term}")
          return False
      
    def replicate_entry(self, key, value):
      """
      Envía la nueva entrada a todos los followers para replicarla.
      """
      for peer in self.peers:
          url = f"http://{peer['host']}:{peer['port']}/append_entries"
          data = {
              "term": self.term,
              "leader_id": self.id,
              "key": key,
              "value": value
          }
          print(f"Líder {self.id}: Replicando entrada a {peer['host']}:{peer['port']} con clave {key} y valor {value}")
          send_post_request(url, data)

    def request_vote(self):
        votes = 1  # El nodo se vota a sí mismo
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/request_vote"
            data = {"term": self.term, "candidate_id": self.id}
            print(f"Nodo {self.id}: Solicitando voto de {peer['host']}:{peer['port']}")
            response = send_post_request(url, data)
            if response and response.get("vote_granted"):
                votes += 1
        return votes

    def start_election(self):
        print(f"Nodo {self.id} iniciando elección en el término {self.term + 1}")
        self.state = "candidate"
        self.term += 1
        self.voted_for = self.id
        votes = self.request_vote()

        if votes > len(self.peers) // 2:
            print(f"Nodo {self.id} ha sido elegido como nuevo líder.")
            self.become_leader()

    def become_leader(self):
        self.state = "leader"
        self.leader_id = self.id
        print(f"Nodo {self.id}: Ahora soy el líder.")
        threading.Thread(target=self.send_heartbeats).start()

    def send_heartbeats(self):
      while self.state == "leader":
          for peer in self.peers:
              url = f"http://{peer['host']}:{peer['port']}/heartbeat"
              data = {
                  "term": self.term,
                  "leader_id": self.id,
                  "leader_logs": self.logs  # Enviar los logs del líder
              }
              print(f"Líder {self.id}: Enviando heartbeat a {peer['host']}:{peer['port']}")
              send_post_request(url, data)
          time.sleep(2)


    def print_state_periodically(self):
        """Imprimir el estado (logs y otros datos) cada cierto tiempo."""
        while True:
            print(f"\n--- Estado del Nodo {self.id} ---")
            print(f"Estado: {self.state}")
            print(f"Término: {self.term}")
            print(f"Líder actual: {self.leader_id}")
            print(f"Logs: {self.logs}")
            time.sleep(5)

    def get_leader_port(self):
        if self.leader_id == self.id:
            return self.port
        else:
            for peer in self.peers:
                if peer['id'] == self.leader_id:
                    return peer['port']
        return None

def send_post_request(url, data):
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al enviar la solicitud POST a {url}: {e}")
    return None

@app.route('/heartbeat', methods=['POST'])
def handle_heartbeat():
    data = request.json
    if not data:
        logger.error("Error: No se recibió ningún dato en la solicitud de heartbeat")
        return jsonify({"error": "No se recibió ningún dato"}), 400

    term = data.get('term')
    leader_id = data.get('leader_id')
    leader_logs = data.get('leader_logs')  # Añadir los logs del líder

    if term is None or leader_id is None or leader_logs is None:
        logger.error("Error: Falta alguno de los parámetros requeridos (term, leader_id, leader_logs) en la solicitud de heartbeat")
        return jsonify({"error": "Parámetros requeridos faltantes"}), 400

    success = node.receive_heartbeat(term, leader_id, leader_logs)
    return jsonify({"success": success})

@app.route('/append_entries', methods=['POST'])
def handle_append_entries():
    data = request.json
    if data is None:
        logger.error("Error: No se recibió ningún dato en la solicitud de append_entries")
        return jsonify({"error": "No se recibió ningún dato"}), 400

    # Verificar que los campos necesarios estén presentes en la solicitud
    term = data.get('term')
    leader_id = data.get('leader_id')
    key = data.get('key')
    value = data.get('value')

    print(f"Solicitud recibida para append_entries en el nodo {node.id}. Term: {term}, Leader ID: {leader_id}, Key: {key}, Value: {value}")

    if term is None or leader_id is None or key is None or value is None:
        logger.error("Error: Falta alguno de los parámetros requeridos (term, leader_id, key, value)")
        return jsonify({"error": "Parámetros requeridos faltantes"}), 400

    # Si este nodo es el líder, actualiza su log y replica la entrada
    if node.state == "leader" and node.id == leader_id:
        success = node.append_entries(term, leader_id, key, value)
        if success:
            print(f"Líder {node.id}: Entrada añadida correctamente. Clave: {key}, Valor: {value}")
            # Replicar la entrada a los followers
            node.replicate_entry(key, value)
            return jsonify({"success": True})
        else:
            logger.error(f"Error al añadir la entrada en el líder {node.id}")
            return jsonify({"error": "Error al añadir la entrada"}), 500
    else:
        # Si no es el líder, es un follower recibiendo una entrada
        success = node.append_entries(term, leader_id, key, value)
        if success:
            print(f"Follower {node.id}: Entrada replicada correctamente. Clave: {key}, Valor: {value}")
            return jsonify({"success": True})
        else:
            logger.error(f"Error al replicar la entrada en el nodo {node.id}")
            return jsonify({"error": "Error al replicar la entrada"}), 500


@app.route('/request_vote', methods=['POST'])
def handle_request_vote():
    data = request.json
    if not data:
        logger.error("Error: No se recibió ningún dato en la solicitud de request_vote")
        return jsonify({"error": "No se recibió ningún dato"}), 400

    term = data.get('term')
    candidate_id = data.get('candidate_id')

    if term is None or candidate_id is None:
        logger.error("Error: Falta alguno de los parámetros requeridos (term, candidate_id) en la solicitud de request_vote")
        return jsonify({"error": "Parámetros requeridos faltantes"}), 400

    if term >= node.term and (node.voted_for is None or node.voted_for == candidate_id):
        node.voted_for = candidate_id
        print(f"Nodo {node.id} votó por {candidate_id} en el término {term}")
        return jsonify({"vote_granted": True})
    return jsonify({"vote_granted": False})

@app.route('/read_data', methods=['GET'])
def handle_read_request():
    key = request.args.get("key")
    if not key:
        logger.error("Error: No se proporcionó ninguna clave en la solicitud de lectura")
        return jsonify({"error": "No se proporcionó ninguna clave"}), 400

    value = node.logs.get(key, None)
    print(f"Nodo {node.id} leyendo clave: {key}, valor: {value}")
    return jsonify({"key": key, "value": value})

@app.route('/get_leader', methods=['GET'])
def get_leader():
    if node.leader_id:
        return jsonify({
            "leader_id": node.leader_id,
            "leader_port": node.get_leader_port(),
            "term": node.term  # Incluir el término actual
        })
    else:
        return jsonify({"leader_id": None, "leader_port": None, "term": None})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "node_id": node.id,
        "state": node.state,
        "term": node.term,
        "leader_id": node.leader_id
    })


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python raft_node.py --id=<id> --port=<puerto>")
        sys.exit(1)

    # Extraer el id y el puerto de los argumentos de la línea de comandos
    id_arg = sys.argv[1]
    port_arg = sys.argv[2]
    node_id = int(id_arg.split('=')[1])
    port = int(port_arg.split('=')[1])

    # Definir peers (modifica según tu configuración)
    peers = [
        {"id": 1, "host": "localhost", "port": 5001},
        {"id": 2, "host": "localhost", "port": 5002},
        {"id": 3, "host": "localhost", "port": 5003}
    ]

    # Remover el nodo actual de la lista de peers
    peers = [peer for peer in peers if peer['id'] != node_id]

    node = RaftNode(node_id, port, peers)
    app.run(port=port)
