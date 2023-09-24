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
from http.server import HTTPServer, BaseHTTPRequestHandler
import scoring


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


class Field(metaclass=abc.ABCMeta):

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def validate_field(self, value):
        """Функция проверяет заполнение поля. Если поле является обязательным,
        но при этом не заполненно, вызывается ошибка ValueError
        Если поле не заполнено, но параметр nullable (возможность установить пустое значение,
        т.е. None, '', [], {}) установлено false, то вызывается ошибка ValueError"""
        if value is None and self.required:
            raise ValueError('Данное поле является обязательным')
        if not value and not self.nullable:
            raise ValueError('Поле не может быть пустым')

    def check_requirements(self, k_rue):
        """Функция проверяет соответствие требованиям для заданного поля."""
        pass

    def check_value_type(self, value):
        """Функция проверяет соответствие типу заявленного для данного поля."""
        return value

    def check_value(self, value):
        """Функция проверяет соответствие требованиям и типу для заявленного поля.
        Сначала вызывается функция валидации заполнения поля. Затем следует вызов проверки типу
        переданных в данное поле. Если проверка на тип пройдена успешно, следует проверка
        на заявленные требования к данным указанным в поле."""
        self.validate_field(value)
        value = self.check_value_type(value)
        
        if not value:
            return value
        self.check_requirements(value)
        return value


class CharField(Field):
    
    def check_value_type(self, value: str):
        if value is not None and not isinstance(value, str):
            raise TypeError('Переданное значение не является строкой')
        return value


class ArgumentsField(Field):

    def check_value_type(self, value: dict):
        if value is not None and not isinstance(value, dict):
            raise TypeError('Переданное значение не является словарем')
        return value


class EmailField(CharField):
    """email - строĸа, в ĸоторой есть @, опционально, может быть пустым"""
    
    def check_requirements(self, value: str):
        super().check_requirements(value)
        pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', re.IGNORECASE)
        match_email = re.fullmatch(pattern, value)
        if not re.fullmatch(pattern, value):
            raise ValueError('Неверный формат адреса почты')


class PhoneField(Field):
    """phone - строĸа или число, длиной 11, начинается с 7, опционально, может быть пустым"""

    def check_value_type(self, value):
        if value is None:
            return value
        if not isinstance(value, (str, int)):
            raise TypeError('Переданное значение не является строкой или целым числом')
        return str(value)
    
    def check_requirements(self, value: str):
        if not str(value).isdigit():
            raise ValueError("Это поле должно содержать только цифры")
        str_value = str(value)
        if str_value[0] != '7' or len(str_value) != 11:
            raise ValueError('Неверный формат номера телефона')




class DateField(CharField):

    def check_value_type(self, value):
        value = super().check_value_type(value)
        if not value:
            return value
        try:
            return datetime.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError('Неверный формат даты. Формат DD.MM.YYYY')
    


class BirthDayField(DateField):
    
    def check_requirements(self, value):
        super().check_requirements(value)
        today = datetime.date.today()
        if (today - value).days / 365.25  > MAX_AGE:
            raise ValueError(f'Превышено максимальное значение возраста, максимально допустимое значение = {MAX_AGE} лет')


class GenderField(Field):

    def check_value_type(self, value: int):
        if value is not None and not isinstance(value, int):
            raise TypeError('Переданное значение не является целым числом. Допустимые значения: 0, 1, 2')
        return value
    
    def check_requirements(self, value: int):
        if value not in GENDERS.keys():
            raise ValueError('Переданное значение пола не является допустимым.')


class ClientIDsField(Field):
    """client_ids - массив чисел, обязательно, не пустое"""

    def check_value_type(self, value: list):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError('Переданное значение не является списком')
            elif [x for x in value if not isinstance(x, int)]:
                raise ValueError('В переданном списке присутствует значения не являющиеся целыми числами.')
        return value
    
    def check_requirements(self, value: list):
         if [x for x in value if x < 0]:
             raise ValueError('В списке присутствуют недопустимые значения.')


class RequestMeta(type):

    """Метакласс в функции __new__ проходит циклом по пространству имен (namespace),
    в них отбирает объекты являющиеся инстансами класса Field (или его потомками).
    Создается новая копия пространства имен, с вложенным отдельным словарем fields_dict."""

    def __new__(cls, name, bases, namespace):
        fields = {}
        for key_namespace, obj in namespace.items():
            if isinstance(obj, Field):
                fields[key_namespace] = obj
        new_namespace = namespace.copy()
        for filed_name in fields:
            del new_namespace[filed_name]
        new_namespace["fields_dict"] = fields
        return super().__new__(cls, name, bases, new_namespace)


class Request(metaclass=RequestMeta):

    def __init__(self, data=None):
        self.fields_errors = None
        self.data = {} if not data else data
        self.non_empty_fields = []
    
    @property
    def errors(self):
        if self.fields_errors is None:
            self.validate()
        return self.fields_errors
    
    def is_valid(self):
        return not self.errors
    
    def validate(self):
        self.fields_errors = {}
        for name, field in self.fields_dict.items():
            try:
                value = self.data.get(name)
                value = field.check_value(value)
                setattr(self, name, value)
                if value not in (None, '', [], (), {}):
                    self.non_empty_fields.append(name)
            except (TypeError, ValueError) as e:
                self.fields_errors[name] = str(e)


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    """Валидация аргументов аргументы валидны, если валидны все поля по
    отдельности и если присутсвует хоть одна пара phone-email, first name-last name,
    gender-birthday с непустыми значениями. Проверяется в функции validate."""
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super().validate()
        if not self.fields_errors:
            if not (self.phone and self.email) and not (self.first_name and self.last_name) and not (self.gender is not None and self.birthday):
                self.fields_errors['arguments'] = 'Присутствуют невалидные аргументы.'
            


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class OnlineScoreHandler:

    """Ответ в ответ выдается число, полученное вызовом фунĸции get_score (см.scoring.py). 
    Но если пользователь админ (см. check_auth), то нужно всегда отдавать 42."""

    def process_request(self, request, context, store):
        r = OnlineScoreRequest(request.arguments)
        if not r.is_valid():
            return r.errors, INVALID_REQUEST
        
        if request.is_admin:
            score = 42
        else:
            score = scoring.get_score(store, r.phone, r.email, r.birthday, r.gender, r.first_name, r.last_name)
        context['has'] = r.non_empty_fields
        return {'score': score}, OK


class ClientsInterestsHandler:

    def process_request(self, request, context, store):
        r = ClientsInterestsRequest(request.arguments)
        if not r.is_valid():
            return r.errors, INVALID_REQUEST
        
        context["nclients"] = len(r.client_ids)
        response_body = {cid: scoring.get_interests(store, cid) for cid in r.client_ids}
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
        "online_score": OnlineScoreHandler,
        "clients_interests": ClientsInterestsHandler
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

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data_string = data_string.decode("utf-8")
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
        self.wfile.write(bytes(json.dumps(r), "utf-8"))
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