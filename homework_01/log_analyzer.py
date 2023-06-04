#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import argparse
from pathlib import Path

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=False, help='config')
    return parser.parse_args()

args = parser()
print(args)





LOG_DIR = os.path.join(Path(__file__).resolve().parent, config.get("LOG_DIR"))

print(os.listdir(LOG_DIR))

with open(f'{LOG_DIR}/nginx-access-ui.log-20170630', 'r') as file:
    for e, line in enumerate(file):
        if e == 0:
            print(line)
        else:
            break



def main():
    pass

if __name__ == "__main__":
    main()
