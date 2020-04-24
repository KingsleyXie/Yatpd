class KHeap:
    def __init__(self, k, cmp ='min'):
        self.k = k
        self.cmp = cmp
        self.list = []

    def __len__(self):
        return len(self.list)

    def __setitem__(self, idx, val):
        self.list[idx] = val

    def __getitem__(self, idx):
        return self.list[idx]

    def __delitem__(self, idx):
        del self.list[idx]

    # Print `K-ary Heap` as a list
    def _print(self):
        print(self.list)

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

    # Restore Down
    def resdown(self, idx):
        tidx = idx
        for cord in range(self.k):
            cidx = self._cidx(idx, cord)
            if cidx < len(self) and self._comp(self[cidx], self[tidx]):
                tidx = cidx
        if (tidx != idx):
            self[tidx], self[idx] = self[idx], self[tidx]
            self.resdown(tidx)

    # Restore Up
    def resup(self, idx):
        while (idx > 0):
            pidx = self._pidx(idx)
            if self._comp(self[idx], self[pidx]):
                self[pidx], self[idx] = self[idx], self[pidx]
            idx = pidx

    # Extract the top element and keep heap properties
    def extracttop(self):
        if not len(self):
            raise Exception('Heap is empty')
        top = self[0]
        self[0] = self[-1]
        del self[-1]
        self.resdown(0)
        return top

    # Insert an element and keep heap properties
    def insert(self, val):
        self.list.append(val)
        self.resup(len(self) - 1)

    # Print all infomation about `K-ary Heap`
    def print(self):
        print(f'{self.k}-ary {self.cmp[0].upper()}{self.cmp[1:].lower()} Heap')
        self._print()
