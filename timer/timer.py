import time
import select
from datetime import datetime

from kheap import KHeap
from rbtree import RBTree


class TObj():
    def __init__(self, timestamp, callback):
        self.timestamp = timestamp
        self.callback = callback

    def __lt__(self, value):
        return self.timestamp < value.timestamp
    def __gt__(self, value):
        return self.timestamp > value.timestamp
    def __ge__(self, value):
        return self.timestamp >= value.timestamp
    def __le__(self, value):
        return self.timestamp <= value.timestamp
    def __eq__(self, value):
        if value:
            return self.timestamp == value.timestamp
        return False


class Timer:
    def __init__(self, ds='kheap', k=4):
        if ds == 'rbtree':
            self.ds = RBTree()
        elif ds == 'kheap':
            self.ds = KHeap(k=k)
        self.epoll = select.epoll()

    @staticmethod
    def realtime_utc_timestamp():
        return int((
            datetime.utcnow() - datetime(1970, 1, 1)
        ).total_seconds() * 1000)

    def run_after(self, sep_ms, cb_handler):
        self.ds.insert(TObj(
            (Timer.realtime_utc_timestamp() + sep_ms),
            cb_handler
        ))

    def start(self):
        while True:
            if not self.ds.gettop():
                break
            curr_nearest = self.ds.gettop().timestamp
            curr_timestamp = Timer.realtime_utc_timestamp()
            if curr_timestamp > curr_nearest:
                min_timeout = curr_timestamp - curr_nearest
                self.epoll.poll(min_timeout / 1000.0)
                dstop = self.ds.gettop()
                while dstop and Timer.realtime_utc_timestamp() > dstop.timestamp:
                    self.ds.extracttop().callback()
                    dstop = self.ds.gettop()


if __name__ == '__main__':
    def utcnow():
        print('Current Timestamp:', Timer.realtime_utc_timestamp())

    timer = Timer(k=6)
    for mst in range(500, 6000, 300):
        timer.run_after(mst, utcnow)
    timer.start()
