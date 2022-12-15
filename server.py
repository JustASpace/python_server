import threading
import socket
from client_thread import ClientThread


class Server(threading.Thread):
    def __init__(self, host, port, server_name, directory):
        threading.Thread.__init__(self)
        self._host = host
        self._port = port
        self._server_name = server_name
        self._directory = directory
        print(f'{server_name} started')

    def run(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()
            while True:
                client_sock, client_address = serv_sock.accept()
                try:
                    new_client_thread = ClientThread(client_sock, client_address, self._directory)
                    new_client_thread.start()
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            serv_sock.close()
