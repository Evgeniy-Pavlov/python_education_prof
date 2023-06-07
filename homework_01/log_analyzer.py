#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import argparse
from pathlib import Path
import re
import datetime
import json
from string import Template
import gzip
import itertools
import statistics


config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "report.html"
}


def parser():
    """Функция парсинга, возвращает аргументы переданные при запуске парсера лога."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=False, help='config', default='./config.json')
    return parser.parse_args()


def set_config(config:dict=config):
    """Функция устанавливающая для конфига параметры переданные функцией parser."""
    if parser() and parser() != './config.json':
        try:
            with open(parser().config) as config_file:
                data = dict(json.load(config_file))
                for key in data.keys:
                    config[key] = data.get(key)
        except FileNotFoundError:
            return config
    return config



def find_last_file(config:dict=config):
    """Функция находит последний по дате в названии nginx-access-ui.log.
    Если находит хотя бы один подходящий файл возвращает последний по 
    времени создания (посление цифры в названии)."""
    LOG_DIR = os.path.join(Path(__file__).resolve().parent, config.get('LOG_DIR'))
    try:
        result = [(file, datetime.datetime.strptime(file[-11:-3], '%Y%m%d').date()) 
            if file.endswith('.gz') else (file, datetime.datetime.strptime(file[-8:], '%Y%m%d').date())
            for file in os.listdir(LOG_DIR) if re.search(r'nginx-access-ui.log-\d{8}.gz', file) or re.search(r'nginx-access-ui.log-\d{8}', file)]
    except FileNotFoundError:
        return None
    result.sort(key= lambda x: x[1], reverse=True)
    return result[0] if result else None



def checking_ability_create_report(config:dict=config):
    """Проверяет возможно ли создать отчет. Отчет возможно создать только если
    последний обработанный по дате отчет меньше чем последний по дате лог. В качестве аргумента
    принимает конфиг."""
    last_file_log = find_last_file(config=config)
    if not last_file_log:
        return 'Логов для обработки не найдено или директория не существует.'
    elif last_file_log:
        REPORT_DIR = os.path.join(Path(__file__).resolve().parent, config.get('REPORT_DIR'))
        try:
            last_report = [(file, datetime.datetime.strptime(file[7:-5], '%Y.%m.%d').date()) 
                for file in os.listdir(REPORT_DIR) if re.search(r'report-\d{4}.\d{2}.\d{2}.html', file)]
        except FileNotFoundError:
            return 'Указанная директория для создания логов не существует.'
        last_report.sort(key= lambda x: x[1], reverse=True)
        if last_report[0][1] == last_file_log[1]:
            return 'Отчет по последнему логу был выгружен. Дополнительная выгрузка не требуется.'
        else:
            return last_report[0][1]


def create_data_for_report(config:dict = config):
    """Функция проходит по файлу лога. Если превышен порог ошибок (20 процентов от текущей длины result),
    то возвращает сообщение об ошибке, отчет далее не сформируется. Если порог ошибок не превышен,
    то возвращает словарь с ключом (url) и значением списком request_time. В качестве аргумента принимает конфиг и
    результат выполнения функции возможности создания отчета (checking_ability_create_report)."""
    LOG_DIR = config.get('LOG_DIR')
    file = find_last_file(config=config)[0]
    file_open = gzip.open(file, mode='rb') if file.endswith('gz') else open(f'{LOG_DIR}/{file}', 'r')
    with file_open as file:
        result = {}
        error_count = 0
        for line in file:
            if error_count < len(result) * 0.2 or len(result) < 10:
                line_list = line.split()
                url, request_time = line_list[6], line_list[-1]
                if url not in result.keys() and re.search(r'/[a-z0-9?=_-]*', url):
                    try:
                        result[url] = [float(request_time)]
                    except ValueError:
                        error_count+=1
                elif not re.search(r'/[a-z0-9?=_-]*', url):
                    error_count+=1
                else:
                    try:
                        result[url].append(float(request_time))
                    except ValueError:
                        error_count+=1
            else:
                return f'Парсинг файла невозможен, превышен порог ошибок. Ошибок зафиксировано: {error_count}.'
        return result



def create_list_for_report(config:dict=config, data_for_report:dict=create_data_for_report(config)):
    """Формирует результирующий список словарей которые будут загружены в отчет. Длина отчета обрезается
    по REPORT_SIZE."""
    all_list_request_time = list(itertools.chain(*data_for_report.values()))
    len_list_request_tume = len(all_list_request_time)
    sum_request_time = sum(all_list_request_time)
    result = [{'url': url, 
            'count': len(data_for_report.get(url)),
            'count_perc': round(len(data_for_report.get(url))/len_list_request_tume, 3),
            'time_sum': round(sum(data_for_report.get(url)),3),
            'time_perc': round(sum(data_for_report.get(url))/sum_request_time, 3),
            'time_avg': round(sum(data_for_report.get(url))/len(data_for_report.get(url)), 3),
            'time_max': max(data_for_report.get(url)),
            'time_med': round(statistics.median(data_for_report.get(url)), 3)} 
            for url in data_for_report.keys()]
    result.sort(key= lambda item: item['time_sum'], reverse=True)
    return result[:config.get('REPORT_SIZE')]
    


def create_report(date:datetime.date, report_list:list, config:dict):
    """Формирует отчет на основе полученных данных из файла."""
    with open(config.get('TEMPLATE')) as temp:
        template_file = Template(temp.read())
    report = template_file.safe_substitute(table_json=json.dumps(report_list))
    report_dir = config.get('REPORT_DIR')
    date_for_report = date.strftime('%Y.%m.%d')
    with open(f'{report_dir}/report-{date_for_report}.html', 'w') as file:
        file.write(report)



def main(config:dict=config):
    config_for_report = set_config(config)
    checking_ability = checking_ability_create_report(config_for_report)
    if isinstance(checking_ability, str):
        print(checking_ability)
    else:
        data_for_report = create_data_for_report(config_for_report)
        if isinstance(data_for_report, str):
            print(data_for_report)
        else:
            result_list = create_list_for_report(config=config_for_report, data_for_report=data_for_report)
            date_for_report = find_last_file(config=config)[1]
            create_report(date=date_for_report, report_list=result_list, config=config_for_report)



if __name__ == "__main__":
    main()
