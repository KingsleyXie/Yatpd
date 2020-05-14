import unittest.main
from heapq import heappush, heappop

from timer.tests.dst import DST
from timer.kheap import KHeap
from timer.rbtree import RBTree


class FuncTest(DST):
    def setUp(self):
        self.kmax = 16
        self.tsize = 300


    def compare(self, ins):
        for dlen in range(1, self.tsize):
            heap = []
            for val in self.get_data(dlen):
                heappush(heap, val)
                ins.insert(val)
            for _ in range(dlen):
                self.assertEqual(
                    heappop(heap),
                    ins.extracttop(),
                    'Top Value Diffs'
                )


class RBTreeTest(FuncTest):
    def test_rbtree(self):
        print(f'\nTesting Red-Black Tree With {self.tsize} Data')
        self.compare(RBTree())


    def test_kheap(self):
        for k in range(2, self.kmax):
            print(f'Testing {k}-ary Heap With {self.tsize} Data')
            self.compare(KHeap(k=k))


if __name__ == '__main__':
    unittest.main()
