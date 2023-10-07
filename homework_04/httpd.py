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


HEADERS = {'Date': datetime.datetime.now(), 'Server': 'MyHTTPServer', 'Content-Length': 9, 'Content-Type': 'text/html', 'Connection': 'close'}

def init_socket(host, port):
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysocket.bind((host, port))
        mysocket.listen(WORKERS)
        return mysocket


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

    def send_response(self):
        self.parse_data()
        print(self.user_headers)
        HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
        content = 'Well done'.encode('utf-8')
        return HDRS.encode('utf-8') + content
        





class MyHTTPServer:
    def __init__(self, host='localhost', port=80):
        self.hostname = host
        self.port = port
        self.mysocket = init_socket(host=host, port=port)
        


    def server_runner(self):
        while True:
            client_socket, address = self.mysocket.accept()
            data = client_socket.recv(1024).decode('utf-8')
            #print(data)
            print(data.split('\r\n'))
            request_handler = RequestHandler(data)
            client_socket.send(request_handler.send_response())
            


if __name__ == '__main__':
    server = MyHTTPServer()
    server.server_runner()
