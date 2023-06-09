import os
import unittest
from log_analyzer import find_last_file, create_data_for_report, create_list_for_report

config_test = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "report.html"
}


class LogParserTest(unittest.TestCase):
    
    def test_find_log_file(self):
        """Проверяет, что функция find_last_file возвращает кортеж, если файлы есть."""
        result = find_last_file(config=config_test)
        assert isinstance(result, tuple)

    
    def test_create_data_for_report(self):
        """Тест проверяет тип возвращаемого значения функции test_create_data_for_report."""
        data_for_report = create_data_for_report(config=config_test)
        assert isinstance(data_for_report, dict)


    def test_field_report(self):
        """Проверяет поля формируемого отчета."""
        data_for_report = create_data_for_report(config=config_test)
        list_result = create_list_for_report(data_for_report=data_for_report, config=config_test)
        assert len(list_result)
        for dict_field in list_result:
            assert set(dict_field.keys()) == {'url', 'count', 'count_perc', 'time_sum', 'time_perc', 'time_avg', 'time_max', 'time_med'}
            assert isinstance(dict_field.get('url'), str)
            assert isinstance(dict_field.get('count'), int)
            assert isinstance(dict_field.get('count_perc'), float)
            assert isinstance(dict_field.get('time_sum'), float)
            assert isinstance(dict_field.get('time_perc'), float)
            assert isinstance(dict_field.get('time_avg'), float)
            assert isinstance(dict_field.get('time_max'), float)
            assert isinstance(dict_field.get('time_med'), float)
    


if __name__=='__main__':
    unittest.main()
