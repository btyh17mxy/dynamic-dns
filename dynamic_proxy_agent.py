#!/usr/bin/env python
# coding: utf-8
import sys
import string
import socket
import signal
import random
import os
import md5
import logging
import time
from lockfile.pidlockfile import PIDLockFile

pidfile_path = "/var/run/dynamic-proxy-agent.pid"
# pidfile_path = "dynamic-proxy-agent.pid"
remote_address = '45.33.51.22'
log = "log"
port = 9999
log_level = logging.INFO
secret = "KJie982jlOAi2fa93"
logging.basicConfig(filename=log, level=log_level)
pidfile = PIDLockFile(pidfile_path)


def on_term(sig, id):
    sys.exit(0)


def make_sum(secret):
    key = ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(42))
    key_md5 = md5.new(key + secret).hexdigest()
    return "%s,%s" % (key, key_md5)


def main():
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, on_term)
        pidfile.acquire()
        while True:
            s = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            s.connect((remote_address, port))
            s.send(make_sum(secret))
            print s.recv(1024)
            s.close()
            time.sleep(10)
            pass
    else:
        signal.signal(signal.SIGTERM, on_term)
        pass


if __name__ == '__main__':
    main()
    # k = make_sum(secret)
    sys.exit(0)
