#!/usr/bin/env python
# coding: utf-8
import sys
import socket
import signal
import os
import logging.handlers
import logging
from lockfile.pidlockfile import PIDLockFile
from config import config
from utils import generate_code, is_code_valid

pidfile = PIDLockFile(
    os.path.join(config.pidfile_path, 'dynamic-proxy-server.pid')
)

last_ip = ''


def on_term(sig, id):
    f_lastip = open(config.lastip_path, 'dynamic-proxy-server-ip')
    f_lastip.write("%s" % last_ip)
    sys.exit(0)


def do_update(new_ip):
    pass


def main():
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, on_term)
        pidfile.acquire()
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((config.listen_ip, config.port))
        serversocket.listen(5)
        while True:
            connection, address = serversocket.accept()
            try:
                connection.settimeout(5)
                buf = connection.recv(1024)
                if is_code_valid(buf.split(',')):
                    # success
                    pass
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
    logging.info(generate_code("adsfasdf"))
    print generate_code("adsfasdf")
    print generate_code("adsfasdf")
    # key = ''.join(
    #     random.SystemRandom().choice(
    #         string.ascii_uppercase + string.digits) for _ in range(42))
    # key_md5 = md5.new(key + secret).hexdigest()
    # print key, key_md5
    # print check_sum("%s,%s" % (key, key_md5))
    sys.exit(0)
