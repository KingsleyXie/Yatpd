# Inspired By Gunicorn's Arbiter
# https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py

import os
import signal
from setproctitle import setproctitle

class Manager(object):
    def __init__(self):
        self.wpids = []
        self.worker_idx = 1
        self.curr_worker = 0
        self.needed_worker = 2
        self.proj_name = 'Yatpd'
        setproctitle(f'{self.proj_name} - Master')

        # REF: https://github.com/benoitc/gunicorn/blob/master/gunicorn/util.py
        def optimize_pipe(fd):
            import fcntl
            fcntl.fcntl(fd, fcntl.F_SETFL, \
                fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)
            fcntl.fcntl(fd, fcntl.F_SETFD, \
                fcntl.fcntl(fd, fcntl.F_GETFD) | fcntl.FD_CLOEXEC)
        self.pipe = os.pipe()
        for side in self.pipe:
            optimize_pipe(side)

        signal.signal(signal.SIGHUP, self.reload)

        self.chgworkers()
        signal.signal(signal.SIGTTIN, self.check)
        signal.signal(signal.SIGTTOU, self.check)
        signal.signal(signal.SIGCHLD, self.killzombies)
        while True:
            pass


    def getwname(self):
        return f'{self.proj_name} - Worker #{self.worker_idx}'

    def reload(self, sig, frame):
        pass

    def check(self, sig, frame):
        if sig == signal.SIGTTIN:
            self.needed_worker += 1
        elif sig == signal.SIGTTOU:
            self.needed_worker -= 1
        if self.needed_worker != self.curr_worker:
            self.chgworkers()


    def chgworkers(self):
        if self.needed_worker > self.curr_worker:
            self.addworkers()
        elif self.needed_worker < self.curr_worker:
            self.delworkers()


    def addworkers(self):
        offset = self.needed_worker - self.curr_worker
        for i in range(offset):
            self.curr_worker += 1
            pid = os.fork()
            if pid == 0:
                setproctitle(self.getwname())
                return
            elif pid > 0:
                self.worker_idx += 1
                self.wpids.append(pid)

    def delworkers(self):
        def kill(pid):
            self.wpids.remove(pid)
            os.kill(pid, signal.SIGKILL)

        pids = self.wpids[:self.curr_worker - self.needed_worker - 1]
        for pid in pids:
            kill(pid)

    def killzombies(self, sig, frame):
        os.waitpid(-1, os.WNOHANG)


m = Manager()
