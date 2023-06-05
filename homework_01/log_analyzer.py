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
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=False, help='config', default='./config.json')
    return parser.parse_args()


def set_config():
    if parser() != './config.json':
        with open(parser()) as config_file:
            data = dict(json.load(config_file))
            for key in data.keys:
                config[key] = data.get(key)
    return config


LOG_DIR = os.path.join(Path(__file__).resolve().parent, config.get("LOG_DIR"))


def find_last_file():
    result = [(file, datetime.datetime.strptime(file[-8:], '%Y%m%d').date()) 
            for file in os.listdir(LOG_DIR) if  re.search(r'nginx-access-ui.log-\d{8}', file)]
    result.sort(key= lambda x: x[1], reverse=True)
    return result[0]



with open(f'{LOG_DIR}/nginx-access-ui.log-20170630', 'r') as file:
    result = {}
    for e, line in enumerate(file):
        if len(result) < config.get('REPORT_SIZE'):
            line_list = line.split()
            if line_list[6] not in result.keys():
                result[line_list[6]] = [float(line_list[-1])]
            else:
                result[line_list[6]].append(float(line_list[-1]))
        else:
            break
    print(result)



def main():
    pass

if __name__ == "__main__":
    main()
