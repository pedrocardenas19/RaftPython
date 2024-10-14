import requests

class Client:
    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    def send_write_command(self, key, value):
        url = f"http://{self.proxy_host}:{self.proxy_port}/client_write"
        response = requests.post(url, json={"key": key, "value": value})
        if response.ok:
            print(f"Respuesta del proxy (escritura): {response.json()}")
        else:
            print("Error en la solicitud de escritura")

    def send_read_request(self, key):
        url = f"http://{self.proxy_host}:{self.proxy_port}/client_read"
        response = requests.get(url, params={"key": key})
        if response.ok:
            print(f"Respuesta del proxy (lectura): {response.json()}")
        else:
            print("Error en la solicitud de lectura")

if __name__ == "__main__":
    client = Client('localhost', 5003)  # El proxy escucha en el puerto 5003
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1: Escribir un par clave-valor")
        print("2: Leer el valor de una clave")
        print("3: Salir")
        
        choice = input("Elige una opción: ")
        
        if choice == '1':
            key = input("Ingresa la clave: ")
            value = input("Ingresa el valor: ")
            client.send_write_command(key, value)
        elif choice == '2':
            key = input("Ingresa la clave para leer el valor: ")
            client.send_read_request(key)
        elif choice == '3':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intenta de nuevo.")
