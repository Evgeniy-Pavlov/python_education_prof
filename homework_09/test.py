import os
import pytest
import collections
from memc_load import dot_rename, parse_appsinstalled

test_data_appsinstalled = ['idfa	1rfw452y52g2gq4g	55.55	42.42	1423,43,567,3,7,23',
                        'idfa	2rfw452y52g2gq4g	55.55	42.42	2423,43,567,3,7,23',
                        'idfa	3rfw452y52g2gq4g	55.55	42.42	3423,43,567,3,7,23',
                        'idfa	4rfw452y52g2gq4g	55.55	42.42	4423,43,567,3,7,23',
                        'idfa	5rfw452y52g2gq4g	55.55	42.42	5423,43,567,3,7,23',
                        'gaid	6rfw452y52g2gq4g	55.55	42.42	6423,43,567,3,7,23',
                        'gaid	7rfw452y52g2gq4g	55.55	42.42	7423,43,567,3,7,23',
                        'gaid	8rfw452y52g2gq4g	55.55	42.42	8423,43,567,3,7,23',
                        'gaid	9rfw452y52g2gq4g	55.55	42.42	9423,43,567,3,7,23',
                        'gaid	10fw452y52g2gq4g	55.55	42.42	1023,43,567,3,7,23']

def test_dot_remame():
    os.mkdir('test_dot_rename')
    test_file = open('test_dot_rename/test_file.txt', 'w')
    test_file.close()
    dot_rename(path='test_dot_rename/test_file.txt')
    assert os.path.isfile('./test_dot_rename/.test_file.txt')

@pytest.mark.parametrize('line', test_data_appsinstalled)
def test_parse_appsinstalled_is_valid_line(line):
    result = parse_appsinstalled(line)
    assert result._fields == ('dev_type', 'dev_id', 'lat', 'lon', 'apps')
    assert isinstance(result.dev_type, str)
    assert isinstance(result.dev_id, str)
    assert isinstance(result.lat, float)
    assert isinstance(result.lon, float)
    assert isinstance(result.apps, list)
    for app in result.apps:
        assert isinstance(app, int)



