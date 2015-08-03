#!/usr/bin/env python
# coding: utf-8
import os
import random
import md5
import string
import logging.handlers
import logging
from mako.template import Template


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
    except ValueError:
        return False


def main():
    secret = "adskjfkk"
    code = generate_code(secret)
    is_valid = is_code_valid(secret, code)
    print code, is_valid
    pass


if __name__ == "__main__":
    template = Template(filename='test.mako', module_directory='')
    # print template.render(ip="1.1.1.1")
    for root, dirs, files in os.walk('/root/code/dynamic-nginx-proxy'):
        for f in files:
            if f.endswith('.mako'):
                print f
        break
    pass
    main()
