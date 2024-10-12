import requests

class Client:
    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    def send_write_command(self, command):
        url = f"http://{self.proxy_host}:{self.proxy_port}/client_write"
        response = requests.post(url, json={"command": command})
        print(f"Respuesta del proxy (escritura): {response.json()}")

    def send_read_request(self):
        url = f"http://{self.proxy_host}:{self.proxy_port}/client_read"
        response = requests.get(url)
        print(f"Respuesta del proxy (lectura): {response.json()}")

if __name__ == "__main__":
    client = Client('localhost', 5003)
    client.send_write_command("Guardar dato importante")
    client.send_read_request()
