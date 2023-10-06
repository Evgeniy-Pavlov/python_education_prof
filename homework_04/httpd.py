import socket
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help='Возвращать файлы по произвольному пути в DOCUMENT_ROOT', default='Evgeniy/ServerDir')
    parser.add_argument('-w', type=int, help='Числов worker\'ов задается аргументом ĸомандной строĸи -w', default=1)
    return parser.parse_args()

parser = parse_arguments()

OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
DOCUMENT_ROOT = parser.f 
WORKERS = parser.w
AVAILABLE_METHODS = ['GET', 'HEAD']
RECV_STEP_SIZE = 10
DELIMETER = b'\r\n\r\n'


def init_socket(host, port):
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.bind((host, port))
    mysocket.listen(10)
    return mysocket

class RequestHandler:
    
    def __init__(self, mysocket):
        self.reqsocket = mysocket
        self.headers = []
        self.body = str()




class MyHTTPServer:
    def __init__(self, host='localhost', port=80):
        self.hostname = host
        self.port = port
        self.mysocket = init_socket(host=host, port=port)

    def server_runner(self):
        while True:
            sock, address = self.mysocket.accept()
            handler = RequestHandler(sock)
