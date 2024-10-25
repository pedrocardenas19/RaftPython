from flask import Flask, request, jsonify
import requests
import random
import logging

app = Flask(__name__)

class Proxy:
    #Constructor -- leader siempre se asigna al primer nodo creado
    def __init__(self, peers):
        self.peers = peers  
        self.leader_url = None 
        self.leader_id = None 
        self.term = 0  
        self.followers = []  


    def update_leader(self):  #Method for updating leader when leader fails or is not available
        print("Intentando actualizar la información del líder...")
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/get_leader"
            print(f"Intentando obtener el líder de {peer['host']}:{peer['port']}")
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    leader_id = data.get('leader_id')
                    leader_port = data.get('leader_port')
                    term = data.get('term')  
                    if leader_id and leader_port and term:
                        self.leader_url = f"http://{peer['host']}:{leader_port}/append_entries"
                        self.leader_id = leader_id
                        self.term = term  
                        print(f"Líder actualizado: {self.leader_url} con leader_id {self.leader_id} y término {self.term}")
                        return
                    else:
                        print(f"No se recibió un líder válido desde {peer['host']}:{peer['port']}")
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener información del nodo {peer['host']}:{peer['port']}: {e}")
        print("No se pudo encontrar un líder disponible.")
        self.leader_url = None
        self.leader_id = None
        self.term = None

    def update_followers(self):
        print("Actualizando la información de los nodos...")
        self.followers = []
        self.leader_id = None
        self.leader_url = None
        self.term = None
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/status"
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    node_id = data.get('node_id')
                    state = data.get('state')
                    if state == "leader":
                        self.leader_id = node_id
                        self.leader_url = f"http://{peer['host']}:{peer['port']}/append_entries"
                        self.term = data.get('term')
                    elif state == "follower":
                        self.followers.append(peer)
            except requests.exceptions.RequestException as e:
                print(f"No se pudo obtener el estado del nodo {peer['id']}: {e}")

    def forward_write_request(self, key, value):
        """
        Reenvía una solicitud de escritura al líder.
        Si falla, actualiza el líder y reintenta la solicitud automáticamente.
        """
        max_retries = 2  # Número máximo de reintentos (1 intento inicial + 1 reintento)
        attempts = 0

        while attempts < max_retries:
            if not self.leader_url:
                print("No se ha detectado un líder, actualizando líder...")
                self.update_leader()

            if self.leader_url:
                print(f"Enviando solicitud de escritura al líder en {self.leader_url}")
                data = {
                    "term": self.term,
                    "leader_id": self.leader_id,
                    "key": key,
                    "value": value
                }
                try:
                    response = requests.post(self.leader_url, json=data)
                    if response.status_code == 200:
                        print(f"Respuesta del líder: {response.json()}")
                        return response.json()
                    else:
                        print(f"Error al comunicarse con el líder. Código de estado: {response.status_code}")
                        # Actualizar líder y reintentar
                        self.update_leader()
                        attempts += 1
                except requests.exceptions.RequestException as e:
                    print(f"Excepción al intentar comunicarse con el líder: {e}")
                    # Actualizar líder y reintentar
                    self.update_leader()
                    attempts += 1
            else:
                print("Error: No se pudo encontrar un líder disponible.")
                return {"error": "No se pudo encontrar un líder disponible"}

        # Si se alcanzó el número máximo de reintentos
        print("Error: No se pudo completar la solicitud después de varios intentos.")
        return {"error": "No se pudo completar la solicitud después de varios intentos"}




    def forward_read_request(self, key):
        """
        Reenvía una solicitud de lectura a un follower disponible.
        Si falla, reintenta con otros followers. Si todos fallan, intenta con el líder.
        Si el líder no está disponible, actualiza la información del líder y reintenta.
        """
        max_retries = len(self.peers)  # Número máximo de intentos
        attempts = 0
        tried_peers = set()

        while attempts < max_retries:
            # Si la lista de followers está vacía o desactualizada, actualizarla
            if not self.followers:
                self.update_followers()

            # Seleccionar un follower no intentado previamente
            available_followers = [peer for peer in self.followers if peer['id'] not in tried_peers]

            if not available_followers:
                break  # No hay más followers para intentar

            follower = random.choice(available_followers)
            tried_peers.add(follower['id'])
            url = f"http://{follower['host']}:{follower['port']}/read_data"
            print(f"Enviando solicitud de lectura a {url} con clave: {key}")

            try:
                response = requests.get(url, params={"key": key}, timeout=2)
                if response.status_code == 200:
                    print(f"Respuesta del follower {follower['id']}: {response.json()}")
                    return response.json()
                else:
                    print(f"Error al comunicarse con el follower {follower['id']}. Código de estado: {response.status_code}")
                    attempts += 1
            except requests.exceptions.RequestException as e:
                print(f"Excepción al intentar comunicarse con el follower {follower['id']}: {e}")
                attempts += 1

        # Si no se pudo leer de ningún follower, intentar con el líder
        if self.leader_url:
            print(f"No se pudo obtener el valor de los followers. Intentando con el líder en {self.leader_url}")
            read_url = self.leader_url.replace('/append_entries', '/read_data')
            try:
                response = requests.get(read_url, params={"key": key}, timeout=2)
                if response.status_code == 200:
                    print(f"Respuesta del líder: {response.json()}")
                    return response.json()
                else:
                    print(f"Error al comunicarse con el líder. Código de estado: {response.status_code}")
                    # Actualizar líder y reintentar una vez
                    self.update_leader()
                    if self.leader_url:
                        read_url = self.leader_url.replace('/append_entries', '/read_data')
                        print(f"Reintentando con el nuevo líder en {self.leader_url}")
                        response = requests.get(read_url, params={"key": key}, timeout=2)
                        if response.status_code == 200:
                            print(f"Respuesta del nuevo líder: {response.json()}")
                            return response.json()
                        else:
                            print(f"Error al comunicarse con el nuevo líder. Código de estado: {response.status_code}")
                    else:
                        print("No se pudo encontrar un líder disponible después de actualizar.")
            except requests.exceptions.RequestException as e:
                print(f"Excepción al intentar comunicarse con el líder: {e}")
                # Actualizar líder y reintentar una vez
                self.update_leader()
                if self.leader_url:
                    read_url = self.leader_url.replace('/append_entries', '/read_data')
                    print(f"Reintentando con el nuevo líder en {self.leader_url}")
                    try:
                        response = requests.get(read_url, params={"key": key}, timeout=2)
                        if response.status_code == 200:
                            print(f"Respuesta del nuevo líder: {response.json()}")
                            return response.json()
                        else:
                            print(f"Error al comunicarse con el nuevo líder. Código de estado: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"Excepción al intentar comunicarse con el nuevo líder: {e}")
                else:
                    print("No se pudo encontrar un líder disponible después de actualizar.")

        # Si todas las solicitudes fallaron, devolver un error al cliente
        print("Error: No se pudo obtener el valor de la clave solicitada.")
        return {"error": "No se pudo obtener el valor de la clave solicitada"}



# Lista de nodos (peers)
#Esto toca añadirle las direcciones ip para la conexion en aws.
peers = [
    {"id": 1, "host": "172.31.41.0", "port": 5001},
    {"id": 2, "host": "172.31.34.27", "port": 5002},
    {"id": 3, "host": "172.31.41.198", "port": 5003}
]


proxy = Proxy(peers)

@app.route('/client_write', methods=['POST'])
def handle_write_request():
    """
    Endpoint para manejar las solicitudes de escritura desde el cliente.
    Recibe un par clave-valor y lo reenvía al líder.
    """
    data = request.json
    key = data.get("key")
    value = data.get("value")
    print(f"Recibida solicitud de escritura del cliente con clave: {key} y valor: {value}")
    response = proxy.forward_write_request(key, value)
    return jsonify(response)

@app.route('/client_read', methods=['GET'])
def handle_read_request():
    """
    Endpoint para manejar las solicitudes de lectura desde el cliente.
    Reenvía la solicitud a uno de los followers.
    """
    key = request.args.get("key")
    print(f"Recibida solicitud de lectura del cliente para la clave: {key}")
    response = proxy.forward_read_request(key)
    return jsonify(response)

if __name__ == "__main__":
    print("Proxy corriendo en el puerto 5004")
    app.run(port=5004)
