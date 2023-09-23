#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
MAX_AGE = 70


class InvalidValueForFieldException(Exception):
    pass


class Field(metaclass=abc.ABCMeta):

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def check_value(self, value):
        self.validate_value(value)
        return value

    def validate_value(self, value):
        pass


class CharField(Field):
    
    def validate_value(self, value: str):
        if isinstance(value, str):
            return value
        else:
            raise TypeError


class ArgumentsField(Field):
    
    def validate_value(self, value: dict):
        online_score_fields = ('phone', 'email', 'first_name', 'last_name', 'birthday', 'gender')
        clients_interests = ('client_ids', 'date')
        if isinstance(value, dict):
            return value
        else:
            raise TypeError
            



class EmailField(CharField):
    
    def validate_value(self, value: str):
        super().validate_value(value)
        regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        match_re = re.match(value, regex_email)
        if match_re:
            return value
        else:
            raise InvalidValueForFieldException('Invalid form email')




class PhoneField(Field):
    
    def validate_value(self, value):
        if isinstance(value, int) or isinstance(value, str):
            number = str(value)
            if not len(number) or (len(number) == 11 and number[0] == '7'):
                return value
            else:
                raise InvalidValueForFieldException('Invalid value for field phone')
        else:
            raise TypeError


class DateField(Field):
    
    def validate_value(self, value):
        try:
            value_date = datetime.datetime.strptime(value, f'%d.%m.%Y')
            return value
        except Exception:
            raise InvalidValueForFieldException('invalid form write of date')


class BirthDayField(DateField):

    def validate_value(self, value):
        super().validate_value(value)
        value_date = datetime.datetime.strptime(value, f'%d.%m.%Y')
        if datetime.datetime.now() - value_date > MAX_AGE:
            raise InvalidValueForFieldException('age exceeds the maximum permissible value')
        else:
            return value


class GenderField(Field):
    
    def validate_value(self, value):
        if isinstance(value, int) and value in GENDERS.keys():
            return value
        elif isinstance(value, int):
            raise KeyError
        else:
            raise InvalidValueForFieldException('Invalid value for field gender')


class ClientIDsField(Field):
    
    def validate_value(self, value):
        if isinstance(value, list) and len(value) == len([x for x in value if isinstance(x, int)]):
            return value
        elif isinstance(value, list):
            raise InvalidValueForFieldException('Not valid value in list')
        else:
            raise TypeError

class MetaRequest(type):
    def __new__(cls, name, bases, namespace):
        fields = {
            filed_name: field
            for filed_name, field in namespace.items()
            if isinstance(field, Field)
        }

        new_namespace = namespace.copy()
        for filed_name in fields:
            del new_namespace[filed_name]
        new_namespace["_fields"] = fields
        return super().__new__(cls, name, bases, new_namespace)


class Request(metaclass=MetaRequest):

    def __init__(self, data=None):
        self._errors = None
        self.data = {} if not data else data
        self.non_empty_fields = []
    
    @property
    def errors(self):
        if self._errors is None:
            self.validate()
        return self._errors
    
    def is_valid(self):
        return not self.errors
    
    def validate(self):
        self._errors = {}

        for name, field in self._fields.items():
            try:
                value = self.data.get(name)
                value = field.validate_value(value)
                setattr(self, name, value)
            except (TypeError, KeyError, InvalidValueForFieldException) as e:
                self._errors[name] = str(e)



class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class OnlineScoreMethodHandler:
    
    def process_request(self, request, context, store):
        r = OnlineScoreRequest(request.arguments)
        if not r.is_valid():
            return r.errors, INVALID_REQUEST
        
        if request.is_admin:
            score = 42
        else:
            score = get_score(store, r.phone, r.email, r.birthday, r.gender, r.first_name, r.last_name)
        context["has"] = r.non_empty_fields
        return {"score": score}, OK


class ClientsIterestsMethodHandler:

    def process_request(self, request, context, store):
        r = ClientsInterestsRequest(request.arguments)
        if not r.is_valid():
            return r.errors, INVALID_REQUEST
        
        context["nclients"] = len(r.client_ids)
        response_body = {}
        return response_body, OK



def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(bytes(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT, "utf-8")).hexdigest()
    else:
        digest = hashlib.sha512(bytes(request.account + request.login + SALT, "utf-8")).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    handlers = {
        "online_score": OnlineScoreMethodHandler,
        "clients_interests": ClientsIterestsMethodHandler
    }

    method_request = MethodRequest(request["body"])
    if not method_request.is_valid():
        return method_request.errors, INVALID_REQUEST
    if not check_auth(method_request):
        return "Forbidden", FORBIDDEN
    
    handler = handlers[method_request.method]()
    return handler.process_request(method_request, ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
