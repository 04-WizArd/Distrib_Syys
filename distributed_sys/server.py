print("serveur!") 
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
