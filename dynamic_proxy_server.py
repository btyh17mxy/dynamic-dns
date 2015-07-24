#!/usr/bin/env python
# coding: utf-8
import sys
import string
import socket
import signal
import random
import os
import md5
import logging.handlers
import logging
from lockfile.pidlockfile import PIDLockFile
# from systemd import journal, daemon
# import time

pidfile_path = "/var/run/dynamic-proxy-server.pid"
log = "log"
listen_address = '45.33.51.22'
port = 9999
log_level = logging.INFO
secret = "KJie982jlOAi2fa93"

logging.basicConfig(filename=log, level=log_level)
pidfile = PIDLockFile(pidfile_path)


def on_term(sig, id):
    sys.exit(0)


def check_sum(key):
    try:
        key, md5sum = key.split(',')
        return md5sum == md5.new(key + secret).hexdigest()
    except ValueError:
        return False


def do_update(new_ip):
    pass


def main():
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, on_term)
        pidfile.acquire()
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((listen_address, port))
        serversocket.listen(5)
        while True:
            connection, address = serversocket.accept()
            try:
                connection.settimeout(5)
                buf = connection.recv(1024)
                if buf == '1':
                    print address
                    connection.send('welcome to server!')
                else:
                    connection.send('fuck off')
            except socket.timeout:
                print 'time out'
            connection.close()
        os._exit(0)
    else:
        signal.signal(signal.SIGTERM, on_term)
        sys.exit(0)


if __name__ == '__main__':
    # main()
    logging.error("this is a error")
    key = ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(42))
    key_md5 = md5.new(key + secret).hexdigest()
    print key, key_md5
    print check_sum("%s,%s" % (key, key_md5))
    sys.exit(0)
