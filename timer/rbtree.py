from timer.ds import DS
from timer.dependency import RedBlackTree


class RBTree(DS):
    def __init__(self, cmp='min'):
        self.tree = RedBlackTree.RedBlackTree()
        self.nil = self.tree.NIL_LEAF
        self.cmp = cmp


    def gettop(self):
        node = self.tree.root
        if not node:
            return None
        if self.cmp == 'min':
            while node and node.left != self.nil:
                node = node.left
        elif self.cmp == 'max':
            while node and node.right != self.nil:
                node = node.right
        else:
            raise Exception('Undefined compare type')
        return node.value


    def extracttop(self):
        top = self.gettop()
        self.tree.remove(top)
        return top


    def insert(self, val):
        self.tree.add(val)


    def print(self):
        print(
            f'Red-Black Tree With {self.cmp.upper()} Compare Type:',
            sep=' '
        )

        queue = [self.tree.root] if self.tree.root else []
        if not queue:
            print('(EMPTY)')
        while queue:
            levellen = len(queue)
            for pos in range(levellen):
                subl, subr = '', ''
                if queue[pos].left != self.nil:
                    queue.append(queue[pos].left)
                    subl = '/'
                if queue[pos].right != self.nil:
                    queue.append(queue[pos].right)
                    subr = '\\'
                end = '\n' if pos == levellen - 1 else '  '
                print(
                    f'{subl}{queue[pos].value}{queue[pos].color[0]}{subr}',
                    end=end
                )
            for _ in range(levellen):
                queue.pop(0)
        print()


if __name__ == '__main__':
    rbt = RBTree()
    testcase = [5, 3, 7, 1, 4, 6, 2]

    for val in testcase:
        print('-' * 50)
        print(f'INSERTING: {val}')
        rbt.insert(val)
        rbt.print()

    for val in testcase:
        print('-' * 50)
        print(f'EXTRACTING: {rbt.extracttop()}')
        rbt.print()
