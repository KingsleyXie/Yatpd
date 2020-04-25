from time import time
from heapq import heappush, heappop

from dst import DST
import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from kheap import KHeap
from rbtree import RBTree

class PerfTest(DST):
    def __init__(self, size, name):
        self.size, self.name = size, name
        self.data = self.get_data(size)
        splitfmt, basefmt = '-' * 73, '|{:^17}|{:^17}|{:^17}|{:^17}|'
        print(splitfmt)
        print(basefmt.format(
            'TEST NAME', 'DATA SIZE',
            'INSERT TIME', 'EXTRACT TIME'
        ))
        self.main()
        print(splitfmt)
        print(basefmt.format(
            self.name, self.size,
            self.instime, self.exttime
        ))
        print(splitfmt)
        print()

    def main(self):
        stime = time()
        self.tinsert()
        mtime = time()
        self.textract()
        etime = time()
        self.instime = round(mtime - stime, 3)
        self.exttime = round(etime - mtime, 3)

    def tinsert(self):
        raise NotImplementedError

    def textract(self):
        raise NotImplementedError

class HeapPerf(PerfTest):
    def __init__(self, size):
        super().__init__(size, 'BUILTIN HEAP')

    def tinsert(self):
        self.heap = []
        for val in self.data:
            heappush(self.heap, val)

    def textract(self):
        for i in range(self.size):
            heappop(self.heap)

class KHeapPerf(PerfTest):
    def __init__(self, size, k):
        super().__init__(size, f'{k}-ARY HEAP')

    def tinsert(self):
        self.kheap = KHeap()
        for val in self.data:
            self.kheap.insert(val)

    def textract(self):
        for i in range(self.size):
            self.kheap.extracttop()

class RBTreePerf(PerfTest):
    def __init__(self, size):
        super().__init__(size, 'RED-BLACK TREE')

    def tinsert(self):
        self.rbtree = RBTree()
        for val in self.data:
            self.rbtree.insert(val)

    def textract(self):
        for i in range(self.size):
            self.rbtree.extracttop()

if __name__ == '__main__':
    for size in [300000]:
        HeapPerf(size=size)
        for k in range(2, 9):
            KHeapPerf(size=size, k=k)
        RBTreePerf(size=size)
