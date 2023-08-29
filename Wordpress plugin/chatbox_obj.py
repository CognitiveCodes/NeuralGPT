import socket

class Chatbox:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send_message(self, message):
        self.socket.sendall(message.encode())

    def receive_message(self):
        data = self.socket.recv(1024)
        return data.decode()

    def close(self):
        self.socket.close()
This code creates a chatbox object that connects to a specified host and port. The send_message method sends a message to the chatbox, while the receive_message method receives a message from the chatbox. The close method closes the connection to the chatbox.

To use the chatbox, you can create an instance of the Chatbox class and call the send_message and receive_message methods as needed. For example:

Copy code

chatbox = Chatbox('localhost', 5021)
chatbox.send_message('Hello, world!')
response = chatbox.receive_message()
print(response)
chatbox.close()