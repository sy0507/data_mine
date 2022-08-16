import os

import fp_growth
import dataloader
from phe import paillier
import time
import numpy as np


def laplace_noisy(sensitivety,epsilon):
    n_value = np.random.laplace(0, sensitivety/epsilon, 1)
    return n_value


def laplace_mech(data, sensitivety, epsilon):
    data +=laplace_noisy(sensitivety, epsilon)
    return data


class Client(object):
    def __init__(self, conf, train_dataset, min_support, min_conf, sub_set_list, support_data):
        self.conf = conf
        self.train_dataset = train_dataset
        self.min_support = min_support
        self.min_conf = min_conf
        self.sub_set_list = sub_set_list
        self.support_data = support_data

    def find_frequent(self):
        spend_time = []
        current_path = os.getcwd()
        if not os.path.exists(current_path+"/log"):
            os.mkdir("log")

        # save_path = current_path+"/log/"+self.id+"_fpgrowth.txt"
        fp = fp_growth.Fp_growth()
        support_data, sub_set_list, rule_list = fp.generate_R(self.train_dataset, self.min_support, self.min_conf)
        # print(self.min_support)
        return sub_set_list, support_data

    def encrypt_HE(self, sub_set, public_key):
        if sub_set not in self.support_data:
            data = 0
            for t in self.train_dataset:
                if sub_set.issubset(frozenset(t)):
                    data += 1
        else:
            data = self.support_data[sub_set]
            time_start_enc = time.time()
        # print(data)
        encrypted_data = public_key.encrypt(data)
        return encrypted_data

    def encrypt_DP(self, sub_set):
        sensitivety = 1
        epsilon = 1
        if sub_set not in self.support_data:
            data = 0
            for t in self.train_dataset:
                if sub_set.issubset(frozenset(t)):
                    data += 1
        else:
            data = self.support_data[sub_set]
        encrypted_data = laplace_mech(data, sensitivety, epsilon)
        if sub_set == frozenset({'root vegetables', 'yogurt'}):
            print(data,encrypted_data)
        return encrypted_data

    def value(self, sub_set):
        if sub_set not in self.support_data:
            data = 0
            for t in self.train_dataset:
                if sub_set.issubset(frozenset(t)):
                    data += 1
        else:
            data = self.support_data[sub_set]
        return data















