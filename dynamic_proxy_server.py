#!/usr/bin/env python
# coding: utf-8
import sys
import socket
import signal
import os
from lockfile.pidlockfile import PIDLockFile
from config import config
from utils import is_code_valid, update_nginx_conf
import logging
from dnspod import Domain, Record

pidfile = PIDLockFile(
    os.path.join(config.pidfile_path, 'dynamic-proxy-server.pid')
)


def on_term(sig, id):
    logging.info('shuting down')
    sys.exit(0)


def write_last_ip(last_ip):
    file_path = os.path.join(config.lastip_path, 'dynamic-proxy-server-ip')
    try:
        f_lastip = open(
            file_path,
            'w'
        )
        f_lastip.write("%s" % last_ip)
    except IOError as e:
        logging.error('fail to write last know ip to %s' % file_path)
        logging.error(e)


def update_dns(last_ip):
    domain = Domain(config.token_id, config.token)
    record = Record(config.token_id, config.token)
    domain_id = domain.domain_id_by_domain(config.domain)
    record_id = record.get_record_id(domain_id, config.sub_domain)
    record.modify(domain_id, record_id, 'A', last_ip,
                  sub_domain=config.sub_domain)


def read_last_ip():
    file_path = os.path.join(config.lastip_path, 'dynamic-proxy-server-ip')
    try:
        f_lastip = open(
            file_path,
            'r'
        )
        return f_lastip.read(-1)
    except IOError as e:
        logging.error(e)

    return ''


def main():
    logging.info('starting up')
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, on_term)
        last_ip = read_last_ip()
        pidfile.acquire()

        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((config.host, config.port))
        serversocket.listen(5)
        logging.info('starting listening at %s port %s' % (
            config.host,
            config.port))
        while True:
            connection, addr = serversocket.accept()
            new_ip = addr[0]
            try:
                connection.settimeout(5)
                buf = connection.recv(1024)
                if is_code_valid(config.secret, buf):
                    if last_ip != new_ip:
                        logging.info('new ip detected %s, do update' % new_ip)
                        update_nginx_conf(new_ip)
                        write_last_ip(new_ip)
                        update_dns(new_ip)
                        last_ip = new_ip
                        connection.send('ok')
                    else:
                        logging.info('ip not change')
                else:
                    logging.warning('secret illegal from  %s' % new_ip)
                    connection.send('fuck off')
            except socket.timeout:
                logging.info('socket time out')
            except socket.error as e:
                logging.error(e)
            connection.close()
    else:
        signal.signal(signal.SIGTERM, on_term)


if __name__ == '__main__':
    main()
    sys.exit(0)
