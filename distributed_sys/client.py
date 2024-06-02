print("client!") 
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
