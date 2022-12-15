import socket
from proxy_client_thread import ProxyClientThread
from configparser import ConfigParser


class ProxyServer():
    def __init__(self, host, port, server_name, available_servers):
        self._host = host
        self._port = port
        self._server_name = server_name
        self._available_servers = available_servers

    def start(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()
            while True:
                client_sock, client_address = serv_sock.accept()
                try:
                    new_client_thread = ProxyClientThread(client_sock, client_address, self._available_servers)
                    new_client_thread.start()
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            serv_sock.close()


config = ConfigParser()
config.read('proxy_config.ini')
proxy_server = ProxyServer(config['proxy_server']['host'],
                           int(config['proxy_server']['port']),
                           config['proxy_server']['server_name'],
                           dict(zip(config['proxy_server']['able_to_connect_names'].split(', '),
                            [int(x) for x in config['proxy_server']['able_to_connect_ports'].split(', ')])))
proxy_server.start()
