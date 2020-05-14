from timer.ds import DS


class KHeap(DS):
    def __init__(self, cmp='min', k=2):
        self.list = []
        self.cmp = cmp
        self.k = k


    # Get parent's index from child's index
    def _pidx(self, cidx):
        return (cidx - 1) // self.k


    # Get child's index from parent's index and child's order
    def _cidx(self, pidx, cord):
        return pidx * self.k + cord + 1


    # Compare using the defined type
    def _comp(self, x, y):
        cmp = self.cmp.lower()
        if cmp == 'min':
            return x < y
        elif cmp == 'max':
            return x > y
        else:
            raise Exception('Undefined compare type')


    # Restore down
    def _resdown(self, idx):
        tidx = idx
        for cord in range(self.k):
            cidx = self._cidx(idx, cord)
            if cidx < len(self.list) \
                    and self._comp(self.list[cidx], self.list[tidx]):
                tidx = cidx
        if (tidx != idx):
            self.list[tidx], self.list[idx] = self.list[idx], self.list[tidx]
            self._resdown(tidx)


    # Restore up
    def _resup(self, idx):
        while (idx > 0):
            pidx = self._pidx(idx)
            if self._comp(self.list[idx], self.list[pidx]):
                self.list[pidx], self.list[idx] = self.list[idx], self.list[pidx]
            idx = pidx


    # Get the top element
    def gettop(self):
        if not len(self.list):
            return None
        return self.list[0]


    # Extract the top element and keep heap properties
    def extracttop(self):
        top = self.gettop()
        self.list[0] = self.list[-1]
        del self.list[-1]
        self._resdown(0)
        return top


    # Insert an element and keep heap properties
    def insert(self, val):
        self.list.append(val)
        self._resup(len(self.list) - 1)


    # Print all infomation about 'K-ary Heap'
    def print(self):
        print(
            f'{self.k}-ary {self.cmp.upper()} Heap',
            self.list,
            sep=': '
        )
        print()


if __name__ == '__main__':
    khp = KHeap()
    testcase = [5, 3, 7, 1, 4, 6, 2]

    for val in testcase:
        print('-' * 50)
        print(f'INSERTING: {val}')
        khp.insert(val)
        khp.print()

    for val in testcase:
        print('-' * 50)
        print(f'EXTRACTING: {khp.extracttop()}')
        khp.print()
