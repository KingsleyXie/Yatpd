from ds import DS
from dependency import RedBlackTree

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
            'Red-Black Tree',
            f'With {self.cmp[0].upper()}{self.cmp[1:].lower()} Compare Type',
            sep=' '
        )
        que = [self.tree.root] if self.tree.root else []
        while que:
            levellen = len(que)
            for i in range(levellen):
                subl, subr = '', ''
                if que[i].left != self.nil:
                    que.append(que[i].left)
                    subl = '/'
                if que[i].right != self.nil:
                    que.append(que[i].right)
                    subr = '\\'
                end = '\n' if i == levellen - 1 else '  '
                print(
                    f'{subl}{que[i].value}{que[i].color[0]}{subr}',
                    end=end
                )
            for i in range(levellen):
                que.pop(0)
