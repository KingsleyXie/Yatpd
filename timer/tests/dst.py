# Data Structure Test Base Class

import random
from unittest import TestCase


class DST(TestCase):
    @property
    def methods(self):
        return [ele for ele in dir(self) \
            if ele.startswith('get_data_with')]


    def get_data(self, needed):
        return self.get_data_with_random_sample(needed)


    def get_data_with_random_sample(self, needed):
        return random.sample(range(needed), needed)


    def get_data_with_random_shuffle(self, needed):
        result = list(range(needed))
        random.shuffle(result)
        return result


    def list_gen(self, needed, optype=''):
        pending, result = list(range(needed)), []
        while needed:
            index = random.randint(0, needed - 1)
            selected = pending[index]

            if optype == 'pop':
                pending.pop(index)
            elif optype == 'remove':
                pending.remove(selected)
            else:
                return

            result.append(selected)
            needed -= 1
        return result


    def get_data_with_list_remove(self, needed):
        return self.list_gen(needed, 'remove')


    def get_data_with_list_pop(self, needed):
        return self.list_gen(needed, 'pop')


if __name__ == '__main__':
    dst = DST()

    func_test_size = 15
    print(f'Current Test Size: {func_test_size}')
    for method in dst.methods:
        data = getattr(dst, method)(func_test_size)
        print(f'METHOD: {method:^35}DATA: {data}')

    perf_test_params = (50000, 100000, 10000)
    from time import process_time
    for perf_test_size in range(*perf_test_params):
        print()
        print('-' * 100)
        print(f'Current Test Size: {perf_test_size}')
        for method in dst.methods:
            start = process_time()
            getattr(dst, method)(perf_test_size)
            cost = round(process_time() - start, 3)
            print(f'METHOD: {method:^35}COST: {cost}')
