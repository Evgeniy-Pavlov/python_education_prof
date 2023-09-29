import pytest
import datetime
import random
from dateutil.relativedelta import relativedelta
from api import Field, CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, GenderField, ClientIDsField, MAX_AGE, GENDERS

empty_values = ['', None, {}, []]
random_values = [1.1, (1, 2), [1, 2], '1', {1, 2}, {'foo': 'bar'}, 1]
str_valid_values = ['Hello', 'world', 'Hello \n world!']
arguments_valid_values = [{'key': 1}, {'foo': 'bar', 'spam': 'eggs'}]
email_invalid_values = ['qwerty@mail', '/*-@mail.com', '@mail.com', 'qwerty@.com', 'qwerty.com', 'кириллический@почта.рф', 'qwerty@mail.c', 'qwerty']
email_valid_values = ['qwerty@mail.ru', 'QwErTy@Mail.Com', 'QWERTY@MAIL.COM', 'qwerty_123@mail.com', 'qwerty@99-9.com']
date_format_invalid_values = ['%Y.%m.%d', '%d.%Y.%m', '%m.%S.%d', '%m.%d.%Y']



def create_date_birthday(valid=True):
    today = datetime.date.today()
    range_date = range(20, MAX_AGE+1, 5) if valid else range(MAX_AGE+1, 100, 5)
    result = [today-relativedelta(years=x) for x in range_date]
    return result


def create_invalid_value_gender():
    result = []
    while len(result) < 3:
        genders = GENDERS.keys()
        randint = random.randint(a=-100, b=100)
        if randint not in genders:
            result.append(randint)
    return result



@pytest.mark.parametrize('data', empty_values)
def test_Field_validate_field_nullable_false(data):
    """Тест проверяет вызов ошибки ValueError, если в поле передается пустое значение, а оно не может быть пустым."""
    test_field = Field(required=False, nullable=False)
    with pytest.raises(ValueError) as err:
        test_field.validate_field(data)
    assert err.value.args[0] == 'Поле не может быть пустым'


def test_Field_validate_value_field_required_true():
    """Тест проверяет вызов ошибки ValueError, если поле является обязательным, но туда передается None."""
    test_field = Field(required=True, nullable=False)
    with pytest.raises(ValueError) as err:
        test_field.validate_field(value=None)
    assert err.value.args[0] == 'Данное поле является обязательным'


@pytest.mark.parametrize('data', empty_values)
def test_field_check_value_valid(data):
    """Проверка выполнения функции check_value для пустых значений, т.к. для класса Field валидация по типам отсутствует.
    В случае отсутствия ошибки возвращает переданное значение."""
    test_field = Field(required=False, nullable=True)
    result = test_field.check_value(value=data)
    assert result is data


@pytest.mark.parametrize('data', [x for x in random_values if not isinstance(x, str)])
def test_CharField_check_value_type_invalid(data):
    """Тест проверяет вызов ошибки TypeError у класса CharField, при передаче в функцию проверки типа данных значений из невалидных типов."""
    test_charfield = CharField()
    with pytest.raises(TypeError) as err:
        test_charfield.check_value_type(data)
    assert err.value.args[0] == 'Переданное значение не является строкой'


@pytest.mark.parametrize('data', str_valid_values)
def test_CharField_check_value_type_valid(data):
    """Тест проверяет, что ошибки TypeError нет при передаче строчного не пустого значения в функцию валидации типа.
    Если значение валидно, то функция возвращает переданное значение."""
    test_charfield = CharField()
    result = test_charfield.check_value_type(data)
    assert result == data


@pytest.mark.parametrize('data', [x for x in random_values if not isinstance(x, dict)])
def test_ArgumentsField_check_value_type_invalid(data):
    """Тест проверяет вызов ошибки TypeError у класса ArgumentsField, при передаче в функцию проверки типа данных значений из невалидных типов."""
    test_argumentsfield = ArgumentsField()
    with pytest.raises(TypeError) as err:
        test_argumentsfield.check_value_type(data)
    assert err.value.args[0] == 'Переданное значение не является словарем'


@pytest.mark.parametrize('data', arguments_valid_values)
def test_ArgumentsField_check_value_type_valid(data):
    """Тест проверяет, что ошибки TypeError нет при передаче словаря в функцию валидации типа.
    Если значение валидно, то функция возвращает переданное значение."""
    test_argumentsfield = ArgumentsField()
    result = test_argumentsfield.check_value_type(data)
    assert result == data
    assert result.items() == data.items()


@pytest.mark.parametrize('data', [x for x in random_values if not isinstance(x, str)])
def test_EmailField_check_value_type_not_str(data):
    """Тест проверяет, что функция проверки валидности эл. почты класса EmailField не принимает не строчные значения.
    В таком случае должна вызываться ошибка TypeError."""
    test_emailfield = EmailField()
    with pytest.raises(TypeError) as err:
        test_emailfield.check_value_type(data)
    assert err.value.args[0] == 'Переданное значение не является строкой'


@pytest.mark.parametrize('data', email_invalid_values)
def test_EmailField_check_requirements_invalid_value(data):
    """Тест проверяет функцию check_requirements класса EmailField, на соответствие требованиям почтового адреса.
    Если адрес не соответствует, функция вызывает ошибку ValueError."""
    test_emailfield = EmailField()
    with pytest.raises(ValueError) as err:
        test_emailfield.check_requirements(data)
    assert err.value.args[0] == 'Неверный формат адреса почты'


@pytest.mark.parametrize('data', email_valid_values)
def test_EmailField_check_requirements_valid_value(data):
    """Тест проверяет, что ошибка ValueError не вызывается при вызове функции check_requirements, если адрес валиданый."""
    test_emailfield = EmailField()
    test_emailfield.check_requirements(data)


@pytest.mark.parametrize('data', [x for x in random_values if not isinstance(x, str)])
def test_DateField_check_value_type_not_str(data):
    """Тест проверяет, что при вызове функции check_value_type, класса DateField, если передано не строчное значение,
    вызывается ошибка TypeError."""
    test_datefield = DateField()
    with pytest.raises(TypeError) as err:
        test_datefield.check_value_type(data)
    assert err.value.args[0] == 'Переданное значение не является строкой'


@pytest.mark.parametrize('format', date_format_invalid_values)
def test_DateField_check_value_type_invalid_format(format):
    """Тест проверяет, что при вызове функции check_value_type, класса DateField, если дата передана в невалидном формате,
    вызывается ошибка ValueError."""
    now_date = datetime.datetime.now()
    result_date = now_date.strftime(format)
    test_datefield = DateField()
    with pytest.raises(ValueError) as err:
        test_datefield.check_value_type(result_date)
    assert err.value.args[0] == 'Неверный формат даты. Формат DD.MM.YYYY'


def test_DateField_check_value_type_valid_format():
    """Тест проверяет, что при передаче даты валидного формата в функцию check_value_type, класса DateField, ошибки нет
    и функция возвращает объект datetime.date."""
    now_date = datetime.datetime.now()
    result_date = now_date.strftime('%d.%m.%Y')
    test_datefield = DateField()
    result = test_datefield.check_value_type(result_date)
    assert isinstance(result, datetime.date)


@pytest.mark.parametrize('date', create_date_birthday(valid=True))
def test_BirthdayField_check_requirements_valid(date):
    """Тест проверяет функцию check_requirements класса BirthdayField. Функция не возвращает ошибку, если переданное значение возвраста
    не превышает MAX_AGE."""
    test_birthdayfield = BirthDayField()
    test_birthdayfield.check_requirements(date)


@pytest.mark.parametrize('date', create_date_birthday(valid=False))
def test_BirthdayField_check_requirements_invalid(date):
    """Тест проверяет вызов ошибки ValueError при выполнении функции check_requirements класса BirthdayField.
    Если переданное значение даты превышает максимальный возраст, то возвщащается ошибка."""
    test_birthdayfield = BirthDayField()
    with pytest.raises(ValueError) as err:
        test_birthdayfield.check_requirements(date)
    assert err.value.args[0] == f'Превышено максимальное значение возраста, \
            максимально допустимое значение = {MAX_AGE} лет'


@pytest.mark.parametrize('gender', [x for x in random_values if not isinstance(x, int)])
def test_GenderField_check_value_type_invalid(gender):
    """Тест проверяет функцию check_value_type класса GenderField. Если значение не является целым числом возвращается
    ошибка TypeError."""
    test_genderfield = GenderField()
    with pytest.raises(TypeError) as err:
        test_genderfield.check_value_type(gender)
    assert err.value.args[0] == 'Переданное значение не является целым числом. Допустимые значения: 0, 1, 2'


@pytest.mark.parametrize('gender', range(0, 3))
def test_GenderField_check_value_type_valid(gender):
    """Тест проверяет функцию check_value_type класса GenderField. Если значение является целым числом, возвращает
    переданное значение."""
    test_genderfield = GenderField()
    result = test_genderfield.check_value_type(gender)
    assert result == gender
    
    
@pytest.mark.parametrize('gender', create_invalid_value_gender())
def test_GenderField_check_requirements_invalid(gender):
    """Тест проверяет функцию check_requirements класса GenderField.
    Если значение невалидно, возвращается ошибка ValueError"""
    test_genderfield = GenderField()
    with pytest.raises(ValueError) as err:
        test_genderfield.check_requirements(gender)
    assert err.value.args[0] == 'Переданное значение пола не является допустимым.'


@pytest.mark.parametrize('gender', GENDERS.keys())
def test_GenderField_check_requirements_valid(gender):
    """Тест проверяет функцию check_requirements класса GenderField.
    Если значение входит в перечень полов (GENDERS), то ошибка вызываться не должна."""
    test_genderfield = GenderField()
    test_genderfield.check_requirements(gender)


@pytest.mark.parametrize('client', [x for x in random_values if not isinstance(x, list)])
def test_ClientsIDsField_check_value_type_invalid_value(client):
    """Тест проверяет функцию check_value_type класса ClientIDsField.
    Если в качестве аргумента передан не список, то возвращает ошибку TypeError."""
    test_clientidsfield = ClientIDsField()
    with pytest.raises(TypeError) as err:
        test_clientidsfield.check_value_type(client)
    assert err.value.args[0] == 'Переданное значение не является списком'

@pytest.mark.parametrize('type_items', [float, str])
def test_ClientsIDsField_check_value_type_invalid_value_in_list(type_items):
    """Тест проверяет функцию check_value_type класса ClientIDsField.
    Если в списке присутствуют значения не являющиеся целыми числами, возвращается ошибка ValueError."""
    test_clientidsfield = ClientIDsField()
    with pytest.raises(ValueError) as err:
        test_clientidsfield.check_value_type([x if x % 2 else type_items(x) for x in range(0, 5)])
    assert err.value.args[0] == 'В переданном списке присутствует значения не являющиеся целыми числами.'


def test_ClientsIDsField_check_value_type_valid_value():
    """Тест проверяет функцию check_value_type класса ClientIDsField.
    Если это список целых чисел, то функция возвращает переданное значение."""
    test_clientidsfield = ClientIDsField()
    result = test_clientidsfield.check_value_type(list(range(0, 3)))
    assert result == list(range(0, 3))