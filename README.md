
# Distributed system

Ce projet Python est conçu pour mettre en place un middleware, un serveur et un client. Le rôle du middleware est de sélectionner dynamiquement un serveur disponible pour exécuter une tâche, en utilisant une logique de répartition de charge. Pour ce faire, nous adopterons une approche simple de type round-robin pour choisir le serveur adéquat.


## Architecture proposé

1. Clients : Envoient des requêtes au middleware.
2. Middleware : Répartit les requêtes entre plusieurs serveurs disponibles de manière équitable.
3. Serveurs : Traitent les requêtes et renvoient les réponses au middleware.

## Code d'implémentation
### Serveur
Différentes instances de ce serveur seront lancées, chacune accédant par un port spécifique.

```bash
import zmq
import sys

def server(port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")

    while True:
        message = socket.recv()
        print(f"Serveur {port} reçu: {message.decode('utf-8')}")
        response = f"Réponse du serveur {port}: {message.decode('utf-8')}"
        socket.send(response.encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = sys.argv[1]
    server(port)

```

### Middleware
Le middleware doit répartir les requêtes entre plusieurs serveurs en utilisant un algorithme de round-robin.
```bash
import zmq
from itertools import cycle

def middleware(server_ports):
    context = zmq.Context()
    
    # Socket pour recevoir les requêtes des clients
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5556")
    
    # Sockets pour communiquer avec les serveurs
    backend_sockets = [context.socket(zmq.DEALER) for _ in server_ports]
    for socket, port in zip(backend_sockets, server_ports):
        socket.connect(f"tcp://localhost:{port}")
    
    # Cycle pour le round-robin
    server_cycle = cycle(backend_sockets)
    
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    for socket in backend_sockets:
        poller.register(socket, zmq.POLLIN)

    while True:
        events = dict(poller.poll())
        
        if frontend in events:
            client_id, empty, client_msg = frontend.recv_multipart()
            server_socket = next(server_cycle)
            server_socket.send_multipart([client_id, b"", client_msg])
        
        for socket in backend_sockets:
            if socket in events:
                reply = socket.recv_multipart()
                frontend.send_multipart(reply)

if __name__ == "__main__":
    server_ports = ["5557", "5558", "5559"]  # Ports des serveurs disponibles
    middleware(server_ports)

```
### Client
```bash 
import zmq

def client(message):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    
    socket.send(message.encode('utf-8'))
    response = socket.recv()
    print(f"Client reçu: {response.decode('utf-8')}")

if __name__ == "__main__":
    client("Hello, Middleware!")
```






## Explication 

1. Serveur:

    -Le serveur écoute sur un port spécifié (5557, 5558, ou 5559).

    -Traite les messages reçus et envoie une    réponse.

2. Middleware:

    -Le middleware utilise des sockets ROUTER pour recevoir les requêtes des clients et DEALER pour envoyer ces requêtes aux serveurs.

    -Il utilise un algorithme de round-robin (cycle de itertools) pour choisir de manière équitable le prochain serveur disponible.

    -Utilise un poller pour gérer les événements des sockets de manière asynchrone.
3. Client:

    -Le client envoie une requête au middleware et attend une réponse.

## Exécution
1. Exécutez plusieurs instances de serveur :
```bash
python server.py 5557
python server.py 5558
python server.py 5559

```
2. Exécutez le middleware:
```bash
python middleware.py

```
3. Exécutez les clients (autant que nécessaire) :
```bash
python client.py

```

