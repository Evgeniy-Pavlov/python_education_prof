import os
import socket
import argparse
import datetime
import mimetypes
from urllib import request, parse
from multiprocessing import Process

OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
HEADERS = {'Date': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z'), 'Server': 'MyHTTPServer',
           'Content-Length': 0, 'Content-Type': 'text/html', 'Connection': 'close'}


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=str, help='Возвращать файлы по произвольному пути в DOCUMENT_ROOT',
                        default='C:/Users/Evgeniy/ServerDir')
    parser.add_argument(
        '-w', type=int, help='Числов worker\'ов задается аргументом ĸомандной строĸи -w', default=1)
    return parser.parse_args()


parser = parse_arguments()
DOCUMENT_ROOT = parser.r
WORKERS = parser.w


class RequestHandler:
    def __init__(self, data):
        self.client_data = data.split('\r\n')
        self.user_headers = {}

    def check_query_params(self):
        list_user_request = self.user_headers['Request'].split('/')
        if '?' in list_user_request[-1]:
            list_user_request[-1] = list_user_request[-1][:
                                                          list_user_request[-1].index('?')]
        return '/'.join(list_user_request)

    def parse_data(self):
        method, request, protocol = self.client_data[0].split(' ')
        self.user_headers['Method'] = method
        self.user_headers['Request'] = parse.unquote(request)
        self.user_headers['Protocol'] = protocol
        if self.user_headers['Request'].endswith('/'):
            self.user_headers['Request'] += 'index.html'
        self.user_headers['Request'] = self.check_query_params()

    def create_headers(self, code, path=None):
        if code == OK:
            HEADERS['Content-Length'] = os.path.getsize(path)
            HEADERS['Content-Type'] = mimetypes.guess_type(
                request.pathname2url(path))[0]
            join_headers = '\r\n'.join(
                [f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {OK} OK\r\n{join_headers}\r\n\r\n'
            return HDRS
        elif code == FORBIDDEN:
            HEADERS['Content-Length'] = os.path.getsize(path)
            HEADERS['Content-Type'] = mimetypes.guess_type(
                request.pathname2url(path))[0]
            join_headers = '\r\n'.join(
                [f'{x[0]}: {x[1]}' for x in HEADERS.items()])
            HDRS = f'HTTP/1.1 {FORBIDDEN} FORBIDDEN\r\n{join_headers}\r\n\r\n'
            return HDRS
        elif code == NOT_FOUND:
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items(
            ) if x[0] not in ('Content-Type', 'Content-Length')])
            HDRS = f'HTTP/1.1 {NOT_FOUND} NOT FOUND\r\n{join_headers}\r\n\r\n'
            return HDRS
        else:
            join_headers = '\r\n'.join([f'{x[0]}: {x[1]}' for x in HEADERS.items(
            ) if x[0] not in ('Content-Type', 'Content-Length')])
            HDRS = f'HTTP/1.1 {METHOD_NOT_ALLOWED} ERROR\r\n{join_headers}\r\n\r\n'
            return HDRS

    def find_attachment(self):
        response = ''
        with open(DOCUMENT_ROOT + self.user_headers['Request'], 'rb') as file:
            response = file.read()
        return response

    def send_response(self):
        try:
            self.parse_data()
        except ValueError:
            HDRS = self.create_headers(code=METHOD_NOT_ALLOWED)
            return HDRS.encode('utf-8')
        if self.user_headers['Method'] == 'GET':
            try:
                HDRS = self.create_headers(
                    code=OK, path=DOCUMENT_ROOT + self.user_headers['Request'])
            except FileNotFoundError:
                HDRS = self.create_headers(code=NOT_FOUND)
                return HDRS.encode('utf-8')
            content = self.find_attachment()
            return HDRS.encode('utf-8') + content
        elif self.user_headers['Method'] == 'HEAD':
            try:
                HDRS = self.create_headers(
                    code=OK, path=DOCUMENT_ROOT + self.user_headers['Request'])
            except FileNotFoundError:
                HDRS = self.create_headers(code=NOT_FOUND)
                return HDRS.encode('utf-8')
            return HDRS.encode('utf-8')
        elif self.user_headers['Method'] not in ('GET', 'HEAD'):
            HDRS = self.create_headers(code=METHOD_NOT_ALLOWED)
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
            client_socket.shutdown(socket.SHUT_WR)
            client_socket.close()


if __name__ == '__main__':
    server = MyHTTPServer()
    process_list = []
    for i in range(WORKERS):
        process = Process(target=server.server_runner)
        process.daemon = True
        process.start()
        process_list.append(process)
    try:
        for process in process_list:
            process.join()
    except KeyboardInterrupt:
        for proc in process_list:
            if proc.is_alive():
                server.mysocket.close()
