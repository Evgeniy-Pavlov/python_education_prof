import hashlib
import datetime
import functools
import pytest
import api

data_bad_auth = [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ]

data_invalid_method_request = [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ]

data_invalid_score_request = [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ]

data_ok_score_request = [
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ]

data_invalid_interests_request = [
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ]

data_ok_iterests_request = [
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ]


@pytest.fixture
def setUp():
    context = {}
    headers = {}
    settings = {}

@setUp
def get_response(request):
    return api.method_handler({"body": request, "headers": headers}, context, settings)


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(bytes(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT, "utf-8")).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(bytes(msg, "utf-8")).hexdigest()


def test_empty_request():
    _, code = get_response({})
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize('data_request', data_bad_auth)    
def test_bad_auth(data_request):
    _, code = get_response(data_request)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize('data_request', data_invalid_method_request)
def test_invalid_method_request(data_request):
    set_valid_auth(data_request)
    response, code = get_response(data_request)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize('arguments', data_invalid_score_request)    
def test_invalid_score_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.INVALID_REQUEST == code
    assert len(response)

@pytest.mark.parametrize('arguments', data_ok_score_request)
def test_ok_score_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.OK == code
    score = response.get("score")
    assert isinstance(score, (int, float)) and score >= 0 and arguments
    assert sorted(context["has"]) == sorted(arguments.keys())

def test_ok_score_admin_request():
    arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
    request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.OK == code
    score = response.get("score")
    assert score == 42


@pytest.mark.parametrize('arguments', data_invalid_interests_request) 
def test_invalid_interests_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.INVALID_REQUEST == code
    assert len(response)

    
def test_ok_interests_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.OK == code
    assert len(arguments["client_ids"]) == len(response)
    assert (all(v and isinstance(v, list) and all(isinstance(i, (bytes, str)) for i in v)
                    for v in response.values()))
    assert context.get("nclients") == len(arguments["client_ids"])


