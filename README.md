# RaftPython
# Tópicos en Telemática

## Paquete → PDU (Protocol Data Unit)
Una PDU representa los datos intercambiados entre capas de un stack de protocolos.

## Stack de Protocolo
Todo lo necesario para establecer comunicación entre dos máquinas.

## Arquitectura de Red
Conjunto de capas que prestan un servicio a la capa inmediatamente superior.

![Arquitectura de Red](https://prod-files-secure.s3.us-west-2.amazonaws.com/7d06eaf4-ca7d-4cd3-b7e6-b539d484f96c/a8a71c04-e177-440c-a5e6-ea83045bd196/Untitled.png)

![Protocolo](https://prod-files-secure.s3.us-west-2.amazonaws.com/7d06eaf4-ca7d-4cd3-b7e6-b539d484f96c/41ae36f0-54d3-4a90-9a47-cfbf68c8cc63/Untitled.png)

---

# Implementación de un Sistema Distribuido Basado en Raft

Este proyecto implementa el algoritmo de consenso **Raft** para un sistema distribuido que maneja pares clave-valor.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Componentes del Sistema](#componentes-del-sistema)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Ejecución del Sistema](#ejecución-del-sistema)
- [Uso del Cliente](#uso-del-cliente)
- [Pruebas y Escenarios](#pruebas-y-escenarios)
- [Consideraciones Adicionales](#consideraciones-adicionales)
- [Referencias](#referencias)

---

## Descripción General

Este sistema distribuido utiliza el algoritmo Raft para mantener la consistencia entre varios nodos. Permite:

- **Escritura y lectura de datos**.
- **Tolerancia a fallos y replicación de datos**.

---

## Componentes del Sistema

### 1. Nodos Raft (`raft_node.py`)

Manejan las elecciones de líder, replicación de logs y heartbeats para sincronización.

### 2. Proxy (`proxy.py`)

Actúa como intermediario entre el cliente y los nodos Raft, manejando solicitudes y fallos.

### 3. Cliente (`client.py`)

Ofrece un menú interactivo para realizar operaciones de lectura y escritura.

---

## Requisitos Previos

- **Python 3.x**.
- Librerías:
  - `Flask`
  - `requests`

Instala las dependencias con:

```bash
pip install -r requirements.txt
