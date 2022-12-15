import threading
from request import Request
from response import Response
from email.parser import Parser
from functools import lru_cache
import pathlib
from pathlib import Path
import os
import logging

logger = logging.getLogger("app.client_thread")

lock = threading.Lock()


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, directory):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.directory = directory
        self.codes = {'Bad request': 400, 'Request line is too long': 414,
                      'Unexpected HTTP version': 400, 'Malformed request line': 400,
                      'Header line is too long': 414, 'Too many headers': 414,
                      'Not found': 404, 'File already exist': 409}
        self.MAX_LINE = 64 * 1024
        self.MAX_HEADERS = 50
        print(f"Connected: {client_address}")

    def run(self):
        try:
            req = self.parse_request()
            self.handle_request(req)
        except Exception as e:
            self.send_response(Response(self.codes[str(e)], str(e)))

    def parse_request(self):
        rfile = self.client_socket.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        if not host:
            raise Exception('Bad request')
        with lock:
            logger.debug(f'{method} {target} {ver}')
            for e, m in headers.items():
                logger.debug(f'{e}: {m}')
        return Request(method, target, ver, headers)

    def parse_request_line(self, rfile):
        raw = rfile.readline(self.MAX_LINE + 1)
        if len(raw) > self.MAX_LINE:
            raise Exception('Request is too long')
        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')
        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')
        return method, target, ver

    def parse_headers(self, rfile):
        headers = []
        while True:
            line = rfile.readline(self.MAX_LINE + 1)
            if len(line) > self.MAX_LINE:
                raise Exception('Header line is too long')
            if line in (b'\r\n', b'\n', b''):
                break
            headers.append(line)
            if len(headers) > self.MAX_HEADERS:
                raise Exception('Too many headers')
        for x in headers:
            print(x)
        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def handle_request(self, req):
        dir_path = pathlib.Path.cwd()
        path = Path(dir_path, self.directory, req.target)
        if req.method == 'GET' and os.path.exists(str(path)):
            self.send_ok_response(Response(200, 'OK'))
            file = self.read_bytes_from_file(path)
            self.client_socket.sendall(file)
            self.client_socket.close()
        elif req.method == 'POST':
            if not os.path.exists(str(path)):
                self.send_ok_response(Response(200, 'OK'))
                f = open(path, 'wb')
                while True:
                    current_bytes = self.client_socket.recv(1024)
                    f.write(current_bytes)
                    if not current_bytes:
                        break
                f.close()
                self.client_socket.close()
            else:
                raise Exception('File already exist')
        else:
            raise Exception('Not found')

    def send_response(self, resp):
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        self.client_socket.send(status_line.encode('iso-8859-1'))
        self.client_socket.close()

    def send_ok_response(self, resp):
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        self.client_socket.send(status_line.encode('iso-8859-1'))

    @lru_cache(maxsize=30)
    def read_bytes_from_file(self, path):
        file_to_bytes = b''
        f = open(path, "rb")
        current_bytes = f.read(1024)
        while current_bytes:
            file_to_bytes += current_bytes
            current_bytes = f.read(1024)
        f.close()
        return file_to_bytes
