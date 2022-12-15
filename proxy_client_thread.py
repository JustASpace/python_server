import logging
import socket
import threading

from response import Response

logger = logging.getLogger("app.client_thread")

lock = threading.Lock()


class ProxyClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, available_servers):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.available_servers = available_servers
        self.codes = {'Bad request': 400, 'Request line is too long': 414,
         'Unexpected HTTP version': 400, 'Malformed request line': 400,
         'Header line is too long': 414, 'Too many headers': 414,
         'Not found': 404, 'File already exist': 409,
                      'Not acceptable' : 406}
        self.extensions = {'jpg': 'image_server', 'txt': 'txt_server',
                           'png': 'image_server'}
        self.MAX_LINE = 64 * 1024
        self.local_server_port = 0
        self.request = b''
        self.method = str()
        print(f"Connected: {client_address}")

    def run(self):
        try:
            rfile, able_to_send = self.parse_request()
            if able_to_send:
                self.send_to_server(rfile)
            else:
                raise Exception('Not acceptable')
        except Exception as e:
            self.send_response(Response(self.codes[str(e)], str(e)))

    def parse_request(self):
        rfile = self.client_socket.makefile('rb')
        able_to_send = self.parse_request_line(rfile)
        return rfile, able_to_send

    def parse_request_line(self, rfile):
        raw = rfile.readline(self.MAX_LINE + 1)
        if len(raw) > self.MAX_LINE:
            raise Exception('Request is too long')
        self.request += raw
        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')
        self.method, target, ver = words
        file_extension = target[target.rfind('.') + 1:]
        if file_extension in self.extensions.keys():
            if self.extensions[file_extension] in self.available_servers.keys():
                self.local_server_port = self.available_servers[self.extensions[file_extension]]
                return True
        return False

    def send_response(self, resp):
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        self.client_socket.send(status_line.encode('iso-8859-1'))

    def send_to_server(self, rfile):
        while True:
            line = rfile.readline(self.MAX_LINE + 1)
            self.request += line
            if line in (b'\r\n', b'\n', b''):
                break
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('127.0.0.1', self.local_server_port))
        server_socket.sendall(self.request)
        if self.method == 'GET':
            while True:
                data = server_socket.recv(1024)
                self.client_socket.send(data)
                if not data:
                    break
        elif self.method == 'POST':
            print("here")
            while True:
                data = self.client_socket.recv(1024)
                print(data)
                server_socket.send(data)
                if not data:
                    break
        status = server_socket.recv(1024)
        self.client_socket.send(status)
