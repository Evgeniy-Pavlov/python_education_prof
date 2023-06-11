#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import re
import json
import gzip
import argparse
import datetime
import logging
import itertools
import statistics
from pathlib import Path
from string import Template

config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "report.html"
}


def parser():
    """Функция парсинга, возвращает аргументы переданные при запуске парсера лога."""
    parser_call = argparse.ArgumentParser()
    parser_call.add_argument('--config', required=False, help='config', default='./config.json')
    return parser_call.parse_args()


def set_config(configuration: dict = config) -> dict:
    """Функция устанавливающая для конфига параметры переданные функцией parser."""
    parser_arg = parser()
    if parser_arg and parser_arg != './config.json':
        try:
            with open(parser_arg.config) as config_file:
                data = dict(json.load(config_file))
                for key in data.keys():
                    configuration[key] = data.get(key)
        except FileNotFoundError:
            return configuration
    return configuration


def set_logging(configuration: dict = config):
    LOGGER = logging.getLogger()
    logging.basicConfig(level=logging.INFO, filename=configuration.get('REPORT_LOG_FILE'),
                        format="[%(asctime)s] %(levelname).1s %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
    return LOGGER


def find_last_file(configuration: dict = config) -> tuple:
    """Функция находит последний по дате в названии nginx-access-ui.log.
    Если находит хотя бы один подходящий файл возвращает последний по 
    времени создания (посление цифры в названии)."""
    LOG_DIR = os.path.join(Path(__file__).resolve().parent, configuration.get('LOG_DIR'))
    try:
        result = [(file, datetime.datetime.strptime(file[-11:-3], '%Y%m%d').date())
                  if file.endswith('.gz') else (file, datetime.datetime.strptime(file[-8:], '%Y%m%d').date())
                  for file in os.listdir(LOG_DIR) if
                  re.search(r'nginx-access-ui.log-\d{8}.gz', file) or re.search(r'nginx-access-ui.log-\d{8}', file)]
    except FileNotFoundError:
        return None
    result.sort(key=lambda x: x[1], reverse=True)
    return result[0] if result else None


def checking_ability_create_report(logger_func, configuration: dict = config) -> bool:
    """Проверяет возможно ли создать отчет. Отчет возможно создать только если
    последний обработанный по дате отчет меньше чем последний по дате лог. В качестве аргумента
    принимает конфиг."""
    last_file_log = find_last_file(configuration=configuration)
    if last_file_log is None or len(last_file_log) == 0:
        logger_func.info(f'Логов для обработки не найдено или директория не существует.')
        return False
    elif last_file_log:
        REPORT_DIR = os.path.join(Path(__file__).resolve().parent, config.get('REPORT_DIR'))
        try:
            last_report = [(file, datetime.datetime.strptime(file[7:-5], '%Y.%m.%d').date())
                           for file in os.listdir(REPORT_DIR) if re.search(r'report-\d{4}.\d{2}.\d{2}.html', file)]
        except FileNotFoundError:
            logger_func.error(f'Указанная директория для создания логов не существует.')
            return False
        last_report.sort(key=lambda x: x[1], reverse=True)
        if not last_report or last_report[0][1] < last_file_log[1]:
            return True
        elif last_report[0][1] == last_file_log[1]:
            logger_func.info('Отчет по последнему логу был выгружен. Дополнительная выгрузка не требуется.')
            return False


def create_data_for_report(logger_func, configuration: dict = config) -> list[dict]:
    """Функция проходит по файлу лога. Если превышен порог ошибок,
    то возвращает сообщение об ошибке, отчет далее не сформируется. Если порог ошибок не превышен,
    то возвращает список словерей (словарь с ключом (url) и значением списком request_time).
    В качестве аргумента принимает конфиг и результат выполнения функции возможности создания 
    отчета (checking_ability_create_report)."""
    LOG_DIR = config.get('LOG_DIR')
    file = find_last_file(configuration=configuration)[0]
    file_open = gzip.open(file, mode='rb') if file.endswith('gz') else open(f'{LOG_DIR}/{file}', 'r')
    with file_open as file:
        result = {}
        error_count = 0
        for line in file:
            if error_count < len(result) or len(result) < 10:
                line_list = line.split()
                url, request_time = line_list[6], line_list[-1]
                if url not in result.keys() and re.search(r'/[a-z0-9?=_-]*', url):
                    try:
                        result[url] = [float(request_time)]
                    except ValueError:
                        error_count += 1
                elif not re.search(r'/[a-z0-9?=_-]*', url):
                    error_count += 1
                else:
                    try:
                        result[url].append(float(request_time))
                    except ValueError:
                        error_count += 1
            else:
                logger_func.error(
                    f'Парсинг файла невозможен, превышен порог ошибок. Ошибок зафиксировано: {error_count}.')
                return None
        return result


def create_list_for_report(logger_func, data_for_report: dict, configuration: dict = config) -> list[dict]:
    """Формирует результирующий список словарей которые будут загружены в отчет. Длина отчета обрезается
    по REPORT_SIZE."""
    all_list_request_time = list(itertools.chain(*data_for_report.values()))
    len_list_request_tume = len(all_list_request_time)
    sum_request_time = sum(all_list_request_time)
    result = [{'url': url,
               'count': len(data_for_report.get(url)),
               'count_perc': round((len(data_for_report.get(url)) / len_list_request_tume) * 100, 3),
               'time_sum': round(sum(data_for_report.get(url)), 3),
               'time_perc': round((sum(data_for_report.get(url)) / sum_request_time) * 100, 3),
               'time_avg': round(sum(data_for_report.get(url)) / len(data_for_report.get(url)), 3),
               'time_max': round(max(data_for_report.get(url)), 3),
               'time_med': round(statistics.median(data_for_report.get(url)), 3)}
              for url in data_for_report.keys()]
    result.sort(key=lambda item: item['time_sum'], reverse=True)
    logger_func.info('Информация из лога собрана, переходим к формированию отчета.')
    return result[:configuration.get('REPORT_SIZE')]


def create_report(logger_func, date: datetime.date, report_list: list, configuration: dict):
    """Формирует отчет на основе полученных данных из файла."""
    with open(configuration.get('TEMPLATE')) as temp:
        template_file = Template(temp.read())
    report = template_file.safe_substitute(table_json=json.dumps(report_list))
    report_dir = configuration.get('REPORT_DIR')
    date_for_report = date.strftime('%Y.%m.%d')
    logger_func.info(f'Отчет будет сформирован в файле {report_dir}/report-{date_for_report}.html')
    with open(f'{report_dir}/report-{date_for_report}.html', 'w') as file:
        file.write(report)


def main(logger_func, configuration: dict = config):
    config_for_report = set_config(configuration)
    logger_func.info('Начинается поиск свежих логов.')
    checking_ability = checking_ability_create_report(logger_func=logger_func, configuration=config_for_report)
    if checking_ability:
        data_for_report = create_data_for_report(configuration=config_for_report, logger_func=logger)
        if data_for_report:
            result_list = create_list_for_report(configuration=config_for_report,
                                                 data_for_report=data_for_report, logger_func=logger)
            date_for_report = find_last_file(configuration=config)[1]
            create_report(date=date_for_report, report_list=result_list,
                          configuration=config_for_report, logger_func=logger)


if __name__ == "__main__":
    set_config(configuration=config)
    logger = set_logging(configuration=config)
    try:
        main(configuration=config, logger_func=logger)
    except Exception as e:
        logger.exception(str(e))
