from phe import paillier
from random import sample

class Server(object):
    def __init__(self, conf, X=0, Y=1, candidate_frequent_itemset={}):# X是下界，Y是上界
        self.candidate_frequent_itemset = candidate_frequent_itemset
        self.X = X
        self.Y = Y
        self.conf = conf

    def generate_key(self, n_length=1024):
        public_key, privacy_key = paillier.generate_paillier_keypair(
            n_length=n_length
        )

        return public_key, privacy_key

    def union(self, sub_set_list):
         for sub_set_item in sub_set_list:
             if frozenset(sub_set_item) not in self.candidate_frequent_itemset:
                 self.candidate_frequent_itemset[frozenset(sub_set_item)] = 1
             else:
                 self.candidate_frequent_itemset[frozenset(sub_set_item)] += 1


# 确定阈值
    def threshold(self):
        self.candidate_frequent_itemset = sorted(self.candidate_frequent_itemset.items(), key=lambda d: d[1])
        count = 0
        for candidate_frequent in self.candidate_frequent_itemset:
            if (candidate_frequent[1]/self.conf['no_models']) >= self.X and (candidate_frequent[1]/self.conf['no_models']) <= self.Y:
                count = count+1
                if count/len(self.candidate_frequent_itemset) >= 0.1:
                    self.X += 0.1
                    self.Y -= 0.1
                    count = 0
                    continue

    def random_sample(self, n, m):
        random_list = {}
        print(n, m)
        for candidate_frequent in self.candidate_frequent_itemset:
            if (candidate_frequent[1]/self.conf['no_models'])>=n and (candidate_frequent[1]/self.conf['no_models'])<=m:
                random_list.update([candidate_frequent])
        return random_list

    def threshold_fix(self, random_list):
        # 随机采样
        items = sample(list(random_list), 5)
        return items


    def get_Jaccard(self,arr1,arr2):
        common = 0
        for item in arr1:
            if item in arr2:
                common += 1
        if common == 0:
            return 0
        # print(set(arr2).difference(set(arr1)))
        return float(common/(len(arr1)+len(arr2)-common))












