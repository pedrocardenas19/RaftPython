from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

class Proxy:
    def __init__(self, peers):
        self.peers = peers  # Lista de nodos (peers)
        self.leader_url = None  # URL del líder actual
        self.leader_id = None  # ID del líder
        self.term = 0  # Término inicial (puedes actualizarlo dinámicamente según tu implementación)

    def update_leader(self):
        print("Intentando actualizar la información del líder...")
        for peer in self.peers:
            url = f"http://{peer['host']}:{peer['port']}/get_leader"
            print(f"Intentando obtener el líder de {peer['host']}:{peer['port']}")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    leader_id = data.get('leader_id')
                    leader_port = data.get('leader_port')
                    term = data.get('term')  # Obtener el término del líder
                    if leader_id and leader_port and term:
                        self.leader_url = f"http://{peer['host']}:{leader_port}/append_entries"
                        self.leader_id = leader_id
                        self.term = term  # Actualizar el término en el proxy
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



    def forward_write_request(self, key, value):
        """
        Reenvía una solicitud de escritura al líder.
        Si no se ha detectado un líder, intenta actualizar la información del líder.
        Si la solicitud falla, intenta actualizar el líder y reintenta la solicitud.
        """
        if not self.leader_url:
            print("No se ha detectado un líder, actualizando líder...")
            self.update_leader()

        if self.leader_url:
            print(f"Enviando solicitud de escritura al líder en {self.leader_url}")
            data = {
                "term": self.term,        # Usar el término actualizado
                "leader_id": self.leader_id,  # Usar el ID del líder actualizado
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
                    # Intentar actualizar el líder y reintentar la solicitud
                    self.update_leader()
                    if self.leader_url:
                        print(f"Reintentando con el nuevo líder en {self.leader_url}")
                        response = requests.post(self.leader_url, json=data)
                        if response.status_code == 200:
                            print(f"Respuesta del nuevo líder: {response.json()}")
                            return response.json()
                        else:
                            print(f"Error al comunicarse con el nuevo líder. Código de estado: {response.status_code}")
                            return {"error": f"Error al comunicarse con el nuevo líder: {response.status_code}"}
                    else:
                        return {"error": "No se pudo encontrar un líder disponible después de actualizar"}
            except requests.exceptions.RequestException as e:
                print(f"Excepción al intentar comunicarse con el líder: {e}")
                # Intentar actualizar el líder y reintentar la solicitud
                self.update_leader()
                if self.leader_url:
                    print(f"Reintentando con el nuevo líder en {self.leader_url}")
                    try:
                        response = requests.post(self.leader_url, json=data)
                        if response.status_code == 200:
                            print(f"Respuesta del nuevo líder: {response.json()}")
                            return response.json()
                        else:
                            print(f"Error al comunicarse con el nuevo líder. Código de estado: {response.status_code}")
                            return {"error": f"Error al comunicarse con el nuevo líder: {response.status_code}"}
                    except requests.exceptions.RequestException as e:
                        print(f"Excepción al intentar comunicarse con el nuevo líder: {e}")
                        return {"error": f"Excepción al intentar comunicarse con el nuevo líder: {str(e)}"}
                else:
                    return {"error": "No se pudo encontrar un líder disponible después de actualizar"}
        else:
            print("Error: No se pudo encontrar un líder disponible.")
            return {"error": "No se pudo encontrar un líder disponible"}



    def forward_read_request(self, key):
        """
        Reenvía una solicitud de lectura a un follower disponible.
        Si todos los followers están caídos, intenta con el líder.
        """
        print(f"Intentando enviar solicitud de lectura para la clave: {key}")

        # Crear una lista de nodos para intentar, excluyendo al líder inicialmente
        nodes_to_try = [peer for peer in self.peers if peer['id'] != self.leader_id]

        # Si no hay followers disponibles, agregar el líder a la lista
        if not nodes_to_try:
            nodes_to_try = [peer for peer in self.peers if peer['id'] == self.leader_id]

        # Intentar enviar la solicitud de lectura a los nodos disponibles
        for peer in nodes_to_try:
            url = f"http://{peer['host']}:{peer['port']}/read_data"
            print(f"Enviando solicitud de lectura a {url} con clave: {key}")
            try:
                response = requests.get(url, params={"key": key}, timeout=2)
                if response.status_code == 200:
                    print(f"Respuesta del nodo {peer['id']}: {response.json()}")
                    return response.json()
                else:
                    print(f"Error al comunicarse con el nodo {peer['id']}. Código de estado: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Excepción al intentar comunicarse con el nodo {peer['id']}: {e}")

        # Si ninguna solicitud tuvo éxito, intentar con el líder
        if self.leader_url:
            print(f"Todos los followers fallaron. Intentando enviar solicitud de lectura al líder en {self.leader_url}")
            try:
                # Reemplazamos '/append_entries' por '/read_data' en la URL del líder
                read_url = self.leader_url.replace('/append_entries', '/read_data')
                response = requests.get(read_url, params={"key": key}, timeout=2)
                if response.status_code == 200:
                    print(f"Respuesta del líder: {response.json()}")
                    return response.json()
                else:
                    print(f"Error al comunicarse con el líder. Código de estado: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Excepción al intentar comunicarse con el líder: {e}")

        # Si todas las solicitudes fallaron, devolver un error al cliente
        print("Error: No se pudo obtener el valor de la clave solicitada.")
        return {"error": "No se pudo obtener el valor de la clave solicitada"}


# Lista de nodos (peers)
peers = [
    {"id": 1, "host": "localhost", "port": 5001},
    {"id": 2, "host": "localhost", "port": 5002},
    {"id": 3, "host": "localhost", "port": 5003}
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
