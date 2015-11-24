#!/usr/bin/env python
# coding: utf-8
import os
import random
import md5
import string
import logging.handlers
import logging
from mako.template import Template
from config import config
log_level = logging.INFO

logging.basicConfig(
    filename=os.path.join(config.logfile_path, 'dynamic-dns-server.log'),
    format='%(asctime)s %(levelname)s %(message)s',
    level=log_level
)


def generate_code(secret):
    key = ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(42))
    key_md5 = md5.new(key + secret).hexdigest()
    return "%s,%s" % (key, key_md5)


def is_code_valid(secret, code):
    try:
        key, md5sum = code.split(',')
        return md5sum == md5.new(key + secret).hexdigest()
    except ValueError as e:
        logging.error('fail to decode')
        logging.error(e)
    return False

def main():
    update_nginx_conf('1.2.2.2')
    pass


if __name__ == "__main__":
    main()
