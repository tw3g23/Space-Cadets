import socket, time

def connect_client(): #Connect client to server
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    host = "localhost"
    print(f"Hostname: {host}")
    port = 50022
    s.connect((host, port))
    return s

def message(): #Initiate connection and send messages to server
    s = connect_client()
    username = input("Please enter your username: ")
    last_message = ""
    while True:
        received = s.recv(1024).decode("utf-8")
        if received != last_message:
            print(received)
        msg = input("Enter your message: ")
        last_message = f'[{username}]> {msg}.'
        s.send(last_message.encode("utf-8"))
        if msg == 'quit':
            print("Quitting.")
            break
    time.sleep(5)
    s.close()

message()