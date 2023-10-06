import socket
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help='Возвращать файлы по произвольному пути в DOCUMENT_ROOT', default='Evgeniy/')
    parser.add_argument('-w', type=int, help='Числов worker\'ов задается аргументом ĸомандной строĸи -w', default=1)
    return parser.parse_args()

parser = parse_arguments()

OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
DOCUMENT_ROOT = parser.f
WORKERS = parser.w


class Server:
    pass