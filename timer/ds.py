# Data Structure Base Class

class DS(object):
    def __init__(self, cmp):
        raise NotImplementedError

    def gettop(self):
        raise NotImplementedError

    def extracttop(self):
        raise NotImplementedError

    def insert(self, val):
        raise NotImplementedError

    def print(self):
        raise NotImplementedError
