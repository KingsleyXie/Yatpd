# Inspired By Gunicorn's Arbiter
# https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py

import os
import sys
import signal
from select import select
from datetime import datetime
from setproctitle import setproctitle


class Manager:
    def __init__(self):
        self.proj_name = 'Yatpd'
        self.log_file = sys.stdout
        self.pipe_rside, self.pipe_wside = os.pipe()

        self.prefix = self.proj_name + ' - '
        setproctitle(f'{self.prefix}Master')
        self.log(f'{self.prefix}Project Starting...')

        self.signal_queue = []
        self.worker_pids = []
        self.pid_name_map = {}
        self.worker_idx = 1
        self.needed_worker = 2
        self.update_workers()

        self.signal_table = {
            signal.SIGTTIN: 'TTIN',
            signal.SIGTTOU: 'TTOU',
            signal.SIGHUP: 'HUP'
        }
        for sig in self.signal_table.keys():
            signal.signal(sig, self.signal_register)
        signal.signal(signal.SIGCHLD, self.child_handler)

        try:
            while True:
                if not self.signal_queue:
                    self.wait_signal()
                else:
                    sig = self.signal_queue.pop(0)
                    getattr(self, f'signal_handler_{sig}', None)()
        except KeyboardInterrupt:
            sys.exit()


    def log(self, content):
        print(f'({datetime.now()}) {content}', file=self.log_file)


    def signal_register(self, sig, frame):
        curr_sig = self.signal_table[sig]
        self.log(f'{self.prefix}Signal {curr_sig} Received')
        self.signal_queue.append(curr_sig.lower())
        self.invoke_handler()


    def child_handler(self, sig, frame):
        os.waitpid(-1, os.WNOHANG)


    def signal_handler_ttin(self):
        self.needed_worker += 1
        self.update_workers()


    def signal_handler_ttou(self):
        self.needed_worker -= 1
        self.update_workers()


    def signal_handler_hup(self):
        pre = self.needed_worker
        self.needed_worker = 0
        self.update_workers()
        self.needed_worker = pre
        self.update_workers()


    def invoke_handler(self):
        os.write(self.pipe_wside, b'Excited!')


    def wait_signal(self):
        ready = select([self.pipe_rside], [], [], 1.0)
        if ready[0]:
            os.read(self.pipe_rside, 8)


    def update_workers(self):
        offset = self.needed_worker - len(self.worker_pids)
        if not offset:
            self.log(f'Called update_workers Without Any Need To Update Workers')
            return

        if offset > 0:
            for _ in range(offset):
                worker_name = f'{self.prefix}Worker #{self.worker_idx}'
                pid = os.fork()
                if pid:
                    self.worker_idx += 1
                    self.worker_pids.append(pid)
                    self.pid_name_map[pid] = worker_name
                    self.log(f'{worker_name} [PID = {pid}] Forked')
                else:
                    self.signal_queue = []
                    setproctitle(worker_name)
                    return
        else:
            def kill_worker(pid):
                worker_name = self.pid_name_map[pid]
                self.worker_pids.remove(pid)
                del self.pid_name_map[pid]

                os.kill(pid, signal.SIGKILL)
                self.log(f'{worker_name} [PID = {pid}] Killed')

            pids = self.worker_pids[:abs(offset)]
            for pid in pids:
                kill_worker(pid)


if __name__ == '__main__':
    manager = Manager()
