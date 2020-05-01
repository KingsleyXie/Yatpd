# Inspired By Gunicorn's Arbiter
# https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py

import os
import signal
from setproctitle import setproctitle

class Manager(object):
    def __init__(self):
        self.worker_cnt = 4
        self.curr_worker = 0
        self.chld_set = 0
        setproctitle('Yatpd - Master')
        self.chgworker()
        signal.signal(signal.SIGTTIN, self.check)
        signal.signal(signal.SIGTTOU, self.check)
        while True:
            pass


    def check(self, sig, frame):
        if sig == signal.SIGTTIN:
            self.worker_cnt += 1
        elif sig == signal.SIGTTOU:
            self.worker_cnt -= 1
        if self.worker_cnt != self.curr_worker:
            self.chgworker()


    def chgworker(self):
        if self.worker_cnt > self.curr_worker:
            self.addworkers()
        elif self.worker_cnt < self.curr_worker:
            self.delworkers()


    def addworkers(self):
        offset = self.worker_cnt - self.curr_worker
        for i in range(offset):
            self.curr_worker += 1
            if os.fork() == 0:
                setproctitle(f'Yatpd - Worker #{self.curr_worker}')
                return
        if not self.chld_set:
            signal.signal(signal.SIGCHLD, self.killzomb)
            self.chld_set = 1


    def delworkers(self):
        pass
        # os.kill(-1, signal.SIGKILL)


    def killzomb(self, sig, frame):
        print('killzomb start')
        os.waitpid(-1, os.WNOHANG)
        print('killzomb end')


m = Manager()
