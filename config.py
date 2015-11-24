#!/usr/bin/env python
# coding: utf-8
from jsob import JsOb
import json


config_file_path = '/etc/dynamic-dns.json'
# config_file_path = 'config.json.sample'
with open(config_file_path, 'r') as f_config:
    config = JsOb(**json.load(f_config))


def main():
    print config
    pass

if __name__ == '__main__':
    main()
