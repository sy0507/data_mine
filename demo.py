import itertools
import random
from itertools import combinations

from phe import paillier # 开源库
import time # 做性能测试

if __name__ == "__main__":

    item_set = frozenset({'whole milk', 'root vegetables','milk'})

    lista = list(itertools.combinations(item_set,2))
    print(lista)
    item = random.sample(lista, 1)
    print(item)

    # for i in combinations(item_set, 2):
    #     print(i)

