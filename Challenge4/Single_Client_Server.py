import socket, time, sys, threading

class Client_connection:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.send_message("Connected to server")

    def get_connection(self):
        return self.connection

    def get_address(self):
        return self.address

    def send_message(self, msg):
        self.connection.send(str.encode(msg))

    def receive_messages(self):
        while True:
            received = self.connection.recv(1024).decode("utf-8")
            print(received)
            self.send_message(received)
            if received.endswith("quit."):
                print("Quitting.")
                break
        return False



class Server:

    def __init__(self):
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        host = "localhost"
        port = 50022
        try:
            self.soc.bind((host, port))
        except socket.error as e:
            print(e)
            time.sleep(10)
            sys.exit()
        self.clients = []
        self.soc.listen(5)  # max socket backlog is 5, this is clients waiting to be accepted


    def receive_client(self):
        print("trying to connect")
        client, address = self.soc.accept()
        print(f'Connected to: {address[0]}:{address[1]}')
        self.clients.append(Client_connection(client, address))
        t1 = (threading.Thread(self.receive_messages(self.clients[len(self.clients)-1])))
        t1.start()


    def receive_messages(self, client):
        while not client.receive_messages():
            self.soc.close()
            sys.exit()



test_server = Server()
test_server.receive_client()