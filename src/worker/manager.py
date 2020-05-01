# Inspired By Gunicorn's Arbiter
# https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py

import os
import signal

class Manager(object):
    def __init__(self):
        self.worker_cnt = 0
        self.curr_worker = 0
        signal.signal(signal.SIGTTIN, self.check(1))
        signal.signal(signal.SIGTTOU, self.check(-1))
        signal.signal(signal.SIGCHLD, self.killzomb())

    def check(self, step):
        self.worker_cnt += step
        if self.worker_cnt > self.curr_worker:
            self.delworkers()
        elif self.worker_cnt < self.curr_worker:
            self.addworkers()

    def addworkers(self):
        offset = self.worker_cnt - self.curr_worker
        for i in range(offset):
            self.curr_worker += 1
            if os.fork() != 0:
                return

    def delworkers(self):
        os.kill(-1)

    def killzomb(self):
        os.waitpid(-1, os.WNOHANG)
