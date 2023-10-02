import pytest
from store import Store
import time

data_for_set = {'foo': 'str', 'spam': 1, 'eggs': 2.2}
data_for_set = {'foo': 321, 'spam': 1, 'eggs': 2.2}

@pytest.mark.parametrize('item', data_for_set.items())
def test_set_value(item):
    connection = Store()
    result = connection.cache_set(key=item[0], value=item[1])
    assert result

@pytest.mark.parametrize('item', data_for_set.items())
def test_set_value_with_seconds(item):
    connection = Store()
    result = connection.cache_set(key=item[0], value=item[1], seconds=3)
    assert result
    time.sleep(3)
    assert not connection.get(item[0])

@pytest.mark.parametrize('item', data_for_set)
def test_get_value(item):
    connection = Store()
    connection.cache_set(key=item[0], value=item[1])
    result = connection.get(item[0])
    assert item[1] == result

@pytest.mark.parametrize('item', data_for_set)
def test_get_value(item):
    connection = Store()
    connection.cache_set(key=item[0], value=item[1])
    result = connection.get(item[0])
    assert item[1] == result
    assert isinstance(result, type(item[0]))

