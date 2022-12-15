import filecmp
import json
import os
import pathlib
import socket
import time
import unittest
from client_thread import ClientThread

dir_path = pathlib.Path.cwd()
IP = "127.0.0.1"

class RawFileMock:
    def __init__(self, lines: list):
        self.count = -1
        self.lines = lines

    def readline(self, n):
        self.count += 1
        return self.lines[self.count]


class SocketMock:
    def __init__(self, raw_file: RawFileMock):
        self.raw_request = raw_file
        self.returned_from_server = b''
        self.returned_response = b''
        self.file_splited = list()
        self.counter = 0
        self.was_readed = False

    def makefile(self, arg):
        return self.raw_request

    def sendall(self, file: bytes):
        self.returned_from_server += file

    def send(self, response: bytes):
        self.returned_response = response

    def recv(self, bytes_to_read: int):
        if not self.was_readed:
            self.get_file(bytes_to_read)
            self.was_readed = True
        else:
            self.counter += 1
        if self.counter >= len(self.file_splited):
            return b''
        return self.file_splited[self.counter]



    def get_file(self, bytes_to_read: int):
        path = pathlib.Path(dir_path, "test_client", "send_to_server.txt")
        file = open(path, "rb")
        current_bytes = file.read(bytes_to_read)
        while current_bytes:
            self.file_splited.append(current_bytes)
            current_bytes = file.read(bytes_to_read)
            if not current_bytes:
                break
        file.close()

    def close(self):
        pass


class ServerTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_file_from_server(self):
        request_raw = [b'GET send_to_client.txt HTTP/1.1\r\n', b'Host: example.local\r\n',
                       b'Client: Python-test\r\n', b'\r\n']
        file = RawFileMock(request_raw)
        client_socket_mock = SocketMock(file)

        ClientThread(client_socket_mock, IP, "test_server").start()
        time.sleep(0.01)

        expected_response = b'HTTP/1.1 200 OK\r\n'
        expected_file = b'Just some text for test.'
        self.assertTrue(expected_file == client_socket_mock.returned_from_server)
        self.assertTrue(expected_response == client_socket_mock.returned_response)

    def test_send_file_to_server(self):
        request_raw = [b'POST returned_from_client.txt HTTP/1.1\r\n', b'Host: example.local\r\n',
                       b'Client: Python-test\r\n', b'\r\n']
        file = RawFileMock(request_raw)
        client_socket_mock = SocketMock(file)

        ClientThread(client_socket_mock, IP, "test_server").start()
        time.sleep(0.01)

        expected_response = b'HTTP/1.1 200 OK\r\n'
        self.assertTrue(expected_response == client_socket_mock.returned_response)
        received_file = pathlib.Path(dir_path, "test_server", "returned_from_client.txt")
        client_file = pathlib.Path(dir_path, "test_client", "send_to_server.txt")
        result = filecmp.cmp(received_file, client_file)
        os.remove(received_file)
        self.assertTrue(result)

