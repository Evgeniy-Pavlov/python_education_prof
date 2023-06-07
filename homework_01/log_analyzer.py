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

config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def parser():
    """Функция парсинга, возвращает аргументы переданные при запуске парсера лога."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=False, help='config', default='./config.json')
    return parser.parse_args()


def set_config():
    """Функция устанавливающая для конфига параметры переданные функцией parser."""
    if parser() != './config.json':
        with open(parser()) as config_file:
            data = dict(json.load(config_file))
            for key in data.keys:
                config[key] = data.get(key)
    return config



def find_last_file(config=config):
    """Функция находит последний по дате в названии nginx-access-ui.log.
    Если находит хотя бы один подходящий файл возвращает последний по 
    времени создания (посление цифры в названии)."""
    LOG_DIR = os.path.join(Path(__file__).resolve().parent, config.get('LOG_DIR'))
    result = [(file, datetime.datetime.strptime(file[-8:], '%Y%m%d').date()) 
            for file in os.listdir(LOG_DIR) if  re.search(r'nginx-access-ui.log-\d{8}', file)]
    result.sort(key= lambda x: x[1], reverse=True)
    return result[0] if result else None



def checking_ability_create_report(config=config):
    last_file_log = find_last_file(config=config)
    if not last_file_log:
        return 'Логов для обработки не найдено'
    elif last_file_log:
        REPORT_DIR = os.path.join(Path(__file__).resolve().parent, config.get('REPORT_DIR'))
        try:
            last_report = [(file, datetime.datetime.strptime(file[7:-5], '%Y.%m.%d').date()) 
                for file in os.listdir(REPORT_DIR) if  re.search(r'report-\d{4}.\d{2}.\d{2}.html', file)]
        except FileNotFoundError:
            return 'Указанная директория для создания логов не существует.'
        last_report.sort(key= lambda x: x[1], reverse=True)
        if last_report[0][1] == last_file_log[1]:
            return 'Отчет по последнему логу был выгружен. Дополнительная выгрузка не требуется.'
        else:
            return last_report[0][1]

print(checking_ability_create_report(config=config))

# with open(f'{LOG_DIR}/{find_last_file()[0]}', 'r') as file:
#     result = {}
#     for e, line in enumerate(file):
#         if len(result) < config.get('REPORT_SIZE'):
#             line_list = line.split()
#             if line_list[6] not in result.keys():
#                 result[line_list[6]] = [float(line_list[-1])]
#             else:
#                 result[line_list[6]].append(float(line_list[-1]))
#         else:
#             break
#     print(result)



def main():
    pass

if __name__ == "__main__":
    main()
