from unittest import main, TestCase
from heapq import heappush, heappop

from kheap import KHeap
from rbtree import RBTree
from tests.datagen import get_data

class FuncTest(TestCase):
    def test_rbtree(self):
        def _test(dlen):
            heap = []
            rbtree = RBTree()
            data = get_data(dlen)
            for val in data:
                heappush(heap, val)
                rbtree.insert(val)
            for i in range(dlen):
                self.assertEqual(
                    heappop(heap),
                    rbtree.extracttop(),
                    'Top Value Diffs: Red-Black Tree'
                )
        for dlen in range(1, 100):
            _test(dlen)
            print(f'Red-Black Tree With {dlen} Data -- Test Passed')

    def test_kheap(self):
        def _test(k, dlen):
            heap = []
            kheap = KHeap(k=k)
            data = get_data(dlen)
            for val in data:
                heappush(heap, val)
                kheap.insert(val)
            for i in range(dlen):
                self.assertEqual(
                    heappop(heap),
                    kheap.extracttop(),
                    f'Top Value Diffs: {k}-ary Heap'
                )
        for k in range(2, 32):
            for dlen in range(1, 100):
                _test(k, dlen)
                print(f'{k}-ary Heap With {dlen} Data -- Test Passed')

if __name__ == '__main__':
    main()
