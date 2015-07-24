#!/usr/bin/env python
# coding: utf-8
import socket

import daemon
from lockfile import pidlockfile

pidfile = pidlockfile.PIDLockFile("/var/run/dynamic-proxy-agent.pid")
with daemon.DaemonContext(pidfile=pidfile):
    main()



def main():
#create an INET, STREAMing socket
    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
#now connect to the web server on port 80
# - the normal http port
    s.connect(("45.33.51.22", 9999))
    s.send('1')  
    print s.recv(1024)
    pass


if __name__ == '__main__':
    main()
