# Data Structure Test Base Class

class DST(object):
    def _get_data(self, needed):
        from random import randint
        pending, result = list(range(needed)), []
        while needed:
            idx = randint(0, needed - 1)
            selected = pending[idx]
            result.append(selected)
            pending.remove(selected)
            needed -= 1
        return result

    def get_data(self, needed):
        from random import sample
        return sample(range(needed), needed)
