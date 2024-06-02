print("middleware!") 
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
