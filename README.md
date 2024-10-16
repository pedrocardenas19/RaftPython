# RaftPython

# Implementación de un Sistema Distribuido Basado en Raft

Este proyecto es una implementación simplificada del algoritmo de consenso **Raft** para un sistema distribuido que maneja operaciones de lectura y escritura de pares clave-valor. El sistema consta de nodos que pueden ser líderes o seguidores, un proxy que actúa como intermediario entre el cliente y los nodos, y un cliente que permite interactuar con el sistema.

## Tabla de Contenidos

- [Descripción General](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Componentes del Sistema](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Requisitos Previos](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Instalación y Configuración](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Ejecución del Sistema](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Uso del Cliente](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Pruebas y Escenarios](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Consideraciones Adicionales](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)
- [Referencias](https://www.notion.so/T-picos-en-Telem-tica-f062389f972d439aa6c91d71d622c66b?pvs=21)

---

## Descripción General

El objetivo de este proyecto es simular un sistema distribuido que utiliza el algoritmo de consenso Raft para mantener la consistencia de datos en múltiples nodos. El sistema permite:

- **Escritura de datos**: Los clientes pueden enviar solicitudes para almacenar pares clave-valor.
- **Lectura de datos**: Los clientes pueden recuperar valores asociados a una clave específica.
- **Tolerancia a fallos**: El sistema maneja caídas de nodos y cambios de líder sin interrumpir el servicio.
- **Replicación de datos**: Los datos escritos en el líder se replican en los seguidores para mantener la consistencia.

---

## Componentes del Sistema

### 1. Nodos Raft (`raft_node.py`)

Cada nodo puede actuar como líder o seguidor. Los nodos manejan:

- **Elecciones de líder**: Los nodos participan en elecciones para determinar el líder.
- **Replicación de logs**: El líder replica las entradas de logs a los seguidores.
- **Manejo de heartbeats**: Los líderes envían heartbeats para mantener a los seguidores sincronizados.

### 2. Proxy (`proxy.py`)

El proxy actúa como intermediario entre el cliente y los nodos Raft:

- **Redirección de solicitudes**: Envía las solicitudes de escritura al líder y las de lectura a los seguidores.
- **Manejo de fallos**: Detecta cambios de líder y actualiza su información para mantener la comunicación.

### 3. Cliente (`client.py`)

El cliente permite interactuar con el sistema:

- **Menú interactivo**: Los usuarios pueden elegir entre operaciones de lectura y escritura.
- **Comunicación con el proxy**: Envía las solicitudes al proxy para su procesamiento.

---

## Requisitos Previos
- **Python 3.10**: Asegúrate de tener Python 3.10 instalado.
- **Librerías Python**:
    - `Flask`: Para crear los servidores HTTP de los nodos y el proxy.
    - `requests`: Para manejar las solicitudes HTTP entre los componentes.
    - `Werkzeug`: Para el manejo de la infraestructura WSGI en los servidores.
    - `Flask-Cors`: Para habilitar Cross-Origin Resource Sharing (CORS).

Instala las librerías necesarias ejecutando:

```bash
bash
Copiar código
pip install -r requirements.txt

```

---

## Instalación y Configuración

1. **Clona este repositorio o descarga los archivos**:
    
    ```bash
    bash
    Copiar código
    git clone https://github.com/tu_usuario/raft-python.git
    cd raft-python
    
    ```
    
2. **Revisa la lista de nodos en los archivos**:
    
    Asegúrate de que la lista de peers (nodos) en `raft_node.py` y `proxy.py` sea coherente y refleje los nodos que vas a ejecutar.
    

---

## Ejecución del Sistema

### 1. Iniciar los Nodos Raft

Cada nodo debe ejecutarse en una terminal separada. A continuación, se muestra cómo iniciar tres nodos:

- **Nodo 1**:
    
    ```bash
    bash
    Copiar código
    python raft_node.py --id=1 --port=5001
    
    ```
    
- **Nodo 2**:
    
    ```bash
    bash
    Copiar código
    python raft_node.py --id=2 --port=5002
    
    ```
    
- **Nodo 3**:
    
    ```bash
    bash
    Copiar código
    python raft_node.py --id=3 --port=5003
    
    ```
    

### 2. Iniciar el Proxy

Ejecuta el proxy en otra terminal:

```bash
bash
Copiar código
python proxy.py

```

### 3. Ejecutar el Cliente

En una nueva terminal, ejecuta el cliente:

```bash
bash
Copiar código
python client.py

```

---

## Uso del Cliente

Al ejecutar `client.py`, verás un menú interactivo:

```markdown
markdown
Copiar código
Seleccione una opción:
1. Escribir un valor
2. Leer un valor
3. Salir

```

### **Opciones Disponibles**

- **1. Escribir un valor**:
    - Se te pedirá ingresar una clave y un valor.
    - El cliente enviará la solicitud de escritura al proxy.
- **2. Leer un valor**:
    - Se te pedirá ingresar la clave que deseas leer.
    - El cliente enviará la solicitud de lectura al proxy.
- **3. Salir**:
    - Cierra el cliente.

---

## Pruebas y Escenarios

### 1. Escritura y Lectura Básica

- **Escribir un par clave-valor**:
    - Ingresa una clave, por ejemplo, `data1`, y un valor, como `hola`.
    - Verifica en las terminales de los nodos que el líder ha replicado la entrada a los seguidores.
- **Leer el valor almacenado**:
    - Ingresa la clave `data1`.
    - El sistema debe devolver el valor `hola`.

### 2. Manejo de Caída del Líder

- **Detener el líder actual**:
    - En la terminal del nodo líder (verifica cuál es por los mensajes en consola), presiona `Ctrl+C` para detenerlo.
- **Realizar una escritura después de la caída del líder**:
    - Sin cerrar el cliente, intenta escribir otro par clave-valor.
    - El proxy detectará la caída del líder, actualizará la información y reintentará la solicitud automáticamente.
- **Verificar que la solicitud fue exitosa**:
    - Observa que la solicitud se procesa correctamente y el nuevo líder maneja la operación.

### 3. Lecturas con Followers Caídos

- **Detener uno o más followers**:
    - Detén los nodos seguidores presionando `Ctrl+C` en sus terminales.
- **Realizar una lectura**:
    - Intenta leer un valor.
    - El proxy intentará comunicarse con los followers disponibles y luego con el líder si es necesario.

### 4. Reincorporación de Nodos

- **Reiniciar nodos detenidos**:
    - Vuelve a ejecutar los nodos que habías detenido.
    - Observa cómo los nodos se sincronizan con el líder actual.

---

## Consideraciones Adicionales

### Manejo de Errores y Logs

- **Logs de Errores**:
    - Los nodos registran errores en el archivo `raft_node_errors.txt`.
    - Puedes revisar este archivo para detalles sobre excepciones o problemas.
- **Mensajes en Consola**:
    - Los nodos y el proxy imprimen mensajes informativos en la consola.
    - Estos mensajes ayudan a entender el estado del sistema y el flujo de operaciones.

### Personalización de Puertos y Nodos

- **Agregar más nodos**:
    - Puedes agregar más nodos al clúster.
    - Asegúrate de actualizar la lista de peers en `raft_node.py` y `proxy.py`.
- **Cambiar direcciones y puertos**:
    - Si deseas ejecutar los nodos en diferentes máquinas o puertos, actualiza las configuraciones en los archivos correspondientes.

### Limitaciones y Mejoras

- **Implementación Simplificada**:
    - Esta implementación es una simplificación del protocolo Raft y no cubre todos los casos de borde.
- **Seguridad y Autenticación**:
    - No se ha implementado autenticación ni seguridad en las comunicaciones.
- **Persistencia de Datos**:
    - Los datos almacenados en los nodos no se persisten en disco y se perderán al detener los nodos.

---

## Referencias

- **Raft Consensus Algorithm**: https://raft.github.io/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Requests Library**: https://requests.readthedocs.io/
