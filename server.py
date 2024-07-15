import socket
import sys
from datetime import datetime
from constants import *

class Server:
    def __init__(self, host='', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.history = []
        self.connected = ""  # save the IP of the client when connection is established

    def create_socket(self):
        """ create a socket """
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print(f"Socket creation error: {e}")
            sys.exit(1)

    def bind_socket(self):
        """ bind socket to port and wait for connection from client """
        try:
            print(f"Binding socket to port: {self.port}")
            self.socket.bind((self.host, self.port))
            self.socket.listen(MAX_QUEUED_CONNECTIONS)  # backlog
        except socket.error as e:
            print(f"Socket binding error: {e}\nRetrying...")
            self.bind_socket()

    def accept_connection(self):
        """ establish a connection with client """
        conn, address = self.socket.accept()
        print(f"Connection created - {address[0]}:{address[1]}")
        self.connected = address[0]
        self.send_commands(conn)
        conn.close()
    
    def send_commands(self, conn):
        """ send commands to the client """
        while True:
            command = input("Enter command: ")
            if self.handle_command(command, conn):
                break

    def handle_command(self, command, conn):
        """ execute the selected command """
        if command == QUIT:
            self.quit_program()
            return True
        elif command == HISTORY:
            self.display_history()
            return False
        if len(command.encode()) > 0:
            conn.send(command.encode())
            client_response = conn.recv(1024).decode("utf-8")
            self.history.append({
                'date': datetime.now().strftime('%d-%m-%Y %H:%M'),
                'content': client_response
            })
            print(client_response, end="")
        return False

    def run(self):
        """ run the server """
        self.create_socket()
        self.bind_socket()
        self.accept_connection()

    def display_history(self):
        """ display the history of received data """
        for entry in self.history:
            print(f"Date: {entry['date']}\nContent:\n{entry['content']}\n{'-'*40}\n")

    def quit_program(self):
        """ save the data collected from the client and exit the program """
        file_name = f"history_{self.connected}_{datetime.now().strftime('%d%m%Y_%H%M')}.txt"
        self.create_data_file(file_name)
        self.socket.close()
        sys.exit()

    def create_data_file(self, file_name):
        """ create a data file and write history data to it """
        try:
            with open(file_name, "w") as data_file:
                for entry in self.history:
                    data_file.write(f"Date: {entry['date']}\nContent:\n{entry['content']}\n{'-'*40}\n")
            print(f"History saved to {file_name}")
        except Exception as e:
            print(f"Error saving history: {e}")

if __name__ == "__main__":
    server = Server()
    server.run()
