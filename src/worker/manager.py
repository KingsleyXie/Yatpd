# Inspired By Gunicorn's Arbiter
# https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py

import os
import sys
import signal
from select import select
from setproctitle import setproctitle

class Manager(object):
    def __init__(self):
        self.proj_name = 'Yatpd'
        self.log_file = sys.stdout
        setproctitle(f'{self.proj_name} - Master')
        print(f'{self.proj_name} - Project Starting...', file=self.log_file)

        self.sig_queue = []
        self.worker_pids = []
        self.worker_idx = 1
        self.curr_worker = 0
        self.needed_worker = 2
        self.chgworkers()

        self.rp, self.wp = os.pipe()

        self.mstable = {
            signal.SIGTTIN: 'ttin',
            signal.SIGTTOU: 'ttou',
            signal.SIGHUP: 'hup'
        }
        for sig in self.mstable.keys():
            signal.signal(sig, self.shandler)
        signal.signal(signal.SIGCHLD, self.killzombies)
        try:
            while True:
                if not self.sig_queue:
                    self.piper()
                else:
                    sig_str = self.mstable[self.sig_queue.pop(0)]
                    getattr(self, f'msh_{sig_str}', None)()
        except KeyboardInterrupt:
            sys.exit()


    def msh_ttin(self):
        self.needed_worker += 1
        self.chgworkers()

    def msh_ttou(self):
        self.needed_worker -= 1
        self.chgworkers()

    def msh_hup(self):
        pre = self.needed_worker
        self.needed_worker = 0
        self.chgworkers()
        self.needed_worker = pre
        self.chgworkers()


    def shandler(self, sig, frame):
        self.sig_queue.append(sig)
        self.pipew()

    def piper(self):
        ready = select([self.rp], [], [], 1.0)
        if ready[0]:
            os.read(self.rp, 8)

    def pipew(self):
        os.write(self.wp, b'Excited!')


    def getwname(self):
        return f'{self.proj_name} - Worker #{self.worker_idx}'

    def chgworkers(self):
        if self.needed_worker > self.curr_worker:
            self.addworkers()
        elif self.needed_worker < self.curr_worker:
            self.delworkers()


    def addworkers(self):
        print(f'Adding worker', file=self.log_file)
        offset = self.needed_worker - self.curr_worker
        for i in range(offset):
            self.curr_worker += 1
            pid = os.fork()
            if pid == 0:
                setproctitle(self.getwname())
                return
            elif pid > 0:
                self.worker_idx += 1
                self.worker_pids.append(pid)


    def delworkers(self):
        def kill(pid):
            self.worker_pids.remove(pid)
            os.kill(pid, signal.SIGKILL)

        print(f'Deleting worker', file=self.log_file)
        pids = self.worker_pids[:self.curr_worker - self.needed_worker - 1]
        for pid in pids:
            kill(pid)


    def killzombies(self, sig, frame):
        os.waitpid(-1, os.WNOHANG)


m = Manager()
