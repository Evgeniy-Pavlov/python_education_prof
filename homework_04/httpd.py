import os
import socket
import argparse
import datetime


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=str, help='Возвращать файлы по произвольному пути в DOCUMENT_ROOT', default='Evgeniy/ServerDir')
    parser.add_argument('-w', type=int, help='Числов worker\'ов задается аргументом ĸомандной строĸи -w', default=1)
    return parser.parse_args()

parser = parse_arguments()

OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
DOCUMENT_ROOT = os.path.abspath(parser.r)
WORKERS = parser.w
AVAILABLE_METHODS = ['GET', 'HEAD']
RECV_STEP_SIZE = 10
DELIMETER = '\r\n'

HEADERS = {'Date': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z'), 'Server': 'MyHTTPServer', 'Content-Length': 0, 'Content-Type': 'text/html', 'Connection': 'close'}



class RequestHandler:
    
    def __init__(self, data):
        self.client_data = data.split('\r\n')
        self.headers = []
        self.body = str()
        self.user_headers = {}

    def parse_data(self):
        method, request, protocol = self.client_data[0].split(' ')
        self.user_headers['Method'] = method
        self.user_headers['Request'] = request
        self.user_headers['Protocol'] = protocol

    def create_headers(self, code, file=None):
        if code == OK:
            HEADERS['Content-Length'] = len(file)
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {OK} OK\r\n{join_headers}\r\n\r\n'
            return HDRS
        elif code == FORBIDDEN:
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {FORBIDDEN} FORBIDDEN\r\n{join_headers}\r\n\r\n'
            return HDRS
        elif code == NOT_FOUND:
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {NOT_FOUND} NOT FOUND\r\n{join_headers}\r\n\r\n'
            return HDRS
        else:
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {METHOD_NOT_ALLOWED} ERROR\r\n{join_headers}\r\n\r\n'
            return HDRS


    def send_response(self):
        self.parse_data()
        print(self.user_headers)
        if self.user_headers['Method'] == 'GET':
            HDRS = self.create_headers(OK, 'Well done')
            content = 'Well done'.encode('utf-8')
            return HDRS.encode('utf-8') + content
        elif self.user_headers['Method'] == 'HEAD':
            HDRS = self.create_headers(OK, 'Well done')
            return HDRS.encode('utf-8')
        else:
            HDRS = self.create_headers(METHOD_NOT_ALLOWED)
            return HDRS.encode('utf-8')


class MyHTTPServer:
    def __init__(self, host='localhost', port=80):
        self.hostname = host
        self.port = port
        self.mysocket = self.init_socket()
        

    def init_socket(self):
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysocket.bind((self.hostname, self.port))
        mysocket.listen(10)
        return mysocket


    def server_runner(self):
        while True:
            client_socket, address = self.mysocket.accept()
            data = client_socket.recv(1024).decode('utf-8')
            request_handler = RequestHandler(data)
            client_socket.send(request_handler.send_response())
            


if __name__ == '__main__':
    server = MyHTTPServer()
    server.server_runner()
