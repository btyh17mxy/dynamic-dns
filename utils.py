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
    filename=os.path.join(config.logfile_path, 'dynamic-proxy-server.log'),
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


def update_nginx_conf(ip):
    for root, dirs, files in os.walk(config.nginx_conf_path):
        for f in files:
            if f.endswith('.mako'):
                mako_file_path = os.path.join(
                    root,
                    f 
                )
                config_file_path = os.path.join(
                    root,
                    "%s.conf" % f.split('.')[0]
                )
                template = Template(filename=mako_file_path, module_directory='/tmp')
                try:
                    f_config = open(
                        config_file_path,
                        'w'
                    )
                    f_config.write(template.render(ip=ip))
                except IOError as e:
                    logging.error('can not write %s' % f_config)
                    logging.error(e)
        break


def main():
    update_nginx_conf('1.2.2.2')
    pass


if __name__ == "__main__":
    main()
