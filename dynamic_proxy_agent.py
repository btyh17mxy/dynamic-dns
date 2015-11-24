#!/usr/bin/env python
# coding: utf-8
import sys
import socket
import signal
import os
import logging
import time
from lockfile.pidlockfile import PIDLockFile
from config import config
from utils import generate_code

pidfile = PIDLockFile(
    os.path.join(config.pidfile_path, 'dynamic-dns-agent.pid')
)


def on_term(sig, id):
    logging.info('shuting down')
    sys.exit(0)


def main():
    logging.info('starting up')
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, on_term)
        pidfile.acquire()
        while True:
            try:
                s = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                s.connect((config.host, config.port))
                s.send(generate_code(config.secret))
                s.close()
                time.sleep(3)
            except socket.error as e:
                logging.error(e)
    else:
        signal.signal(signal.SIGTERM, on_term)


if __name__ == '__main__':
    main()
    sys.exit(0)
