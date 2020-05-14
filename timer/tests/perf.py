import unittest.main
from time import process_time
from heapq import heappush, heappop

from timer.tests.dst import DST
from timer.kheap import KHeap
from timer.rbtree import RBTree


class PerfTest(DST):
    def setUp(self, name=None, krange=None):
        self.name, self.krange = name, krange
        self.size = 100000
        self.data = self.get_data(self.size)


    def test_perf(self):
        if not self.name:
            return

        if self.krange:
            postfix = self.name
            for k in self.krange:
                self.name = f'{k}{postfix}'
                self.calc(k)
        else:
            self.calc()


    def calc(self, k=None):
        stime = process_time()
        self.tinsert(k) if k else self.tinsert()
        mtime = process_time()
        self.textract()
        etime = process_time()
        self.instime = round(mtime - stime, 3)
        self.exttime = round(etime - mtime, 3)
        self.print()


    def print(self):
        splitfmt, basefmt = '-' * 73, '|{:^17}|{:^17}|{:^17}|{:^17}|'
        print()
        print(splitfmt)
        print(basefmt.format(
            'TEST NAME', 'DATA SIZE',
            'INSERT TIME', 'EXTRACT TIME'
        ))
        print(splitfmt)
        print(basefmt.format(
            self.name, self.size,
            self.instime, self.exttime
        ))
        print(splitfmt)


    def tinsert(self):
        raise NotImplementedError


    def textract(self):
        raise NotImplementedError


class HeapPerf(PerfTest):
    def setUp(self):
        return super().setUp('BUILTIN HEAP')


    def tinsert(self):
        self.heap = []
        for val in self.data:
            heappush(self.heap, val)


    def textract(self):
        for i in range(self.size):
            heappop(self.heap)


class KHeapPerf(PerfTest):
    def setUp(self):
        return super().setUp(f'-ARY HEAP', range(2, 9))


    def tinsert(self, k):
        self.kheap = KHeap(k=k)
        for val in self.data:
            self.kheap.insert(val)


    def textract(self):
        for i in range(self.size):
            self.kheap.extracttop()


class RBTreePerf(PerfTest):
    def setUp(self):
        return super().setUp('RED-BLACK TREE')


    def tinsert(self):
        self.rbtree = RBTree()
        for val in self.data:
            self.rbtree.insert(val)


    def textract(self):
        for i in range(self.size):
            self.rbtree.extracttop()


if __name__ == '__main__':
    unittest.main()
