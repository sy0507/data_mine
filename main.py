import argparse
import json
import math
import os
from random import random
import server
import client
import dataloader
import random
import itertools
import time


start_time = time.time()

parser = argparse.ArgumentParser(description='Federated Learning')
parser.add_argument('--conf', dest='conf')
args = parser.parse_args()

print(args)

with open(args.conf, 'r') as f:
    conf = json.load(f)
filename = "groceries.csv"
min_support = 0.03
min_conf = 0.7
current_path = os.getcwd()
path = current_path+"/dataset/"+filename

data_set = dataloader.load_data(path)
length = len(data_set)
print(length)
clients = []
server = server.Server(conf)
for c in range(conf["no_models"]):
    one_list = data_set[math.floor(c/conf["no_models"]*length):math.floor((c+1) / conf["no_models"]*length)]
    length_client = len(one_list)
    clients.append(client.Client(conf, one_list, min_support * length_client, min_conf, 0, 0))

public_key, private_key = server.generate_key()
# 每个客户端求出局部频繁项集
for c in clients:
    sub_set_list, support_data = c.find_frequent()
    c.support_data = support_data
    c.sub_set_list = sub_set_list
    # print(c.sub_set_list)
# 求出候选频繁项集
for c in clients:
    server.union(c.sub_set_list)

server.threshold()  # 阈值初值确定


# value_frequent_itemset = []
# for candidate_frequent in server.candidate_frequent_itemset:
#     value_support_data = 0
#     for c in clients:
#         value_support_data += c.value(candidate_frequent[0])
#     if value_support_data >= (min_support * length):
#         value_frequent_itemset.append(candidate_frequent[0])
# end_time = time.time()
# print("耗时: {:.2f}秒".format(end_time - start_time))
# 下界
while(1):
    random_list = server.random_sample(round(server.X - 0.1, 4), server.X)
    random_items = server.threshold_fix(random_list)
    print(random_items)
    false_no = 0
    for random_item in random_items:
        data_support = 0
        for c in clients:
            data_support += c.encrypt_DP(random_item)
        if data_support < (min_support*length):
            false_no += 1
    if false_no >= 4:
        print(round(server.X, 4))
        break
    else:
        server.X -= 0.1
# 上界
while(1):
    random_list = server.random_sample(round(server.Y, 4), round(server.Y+0.1, 4))
    random_items = server.threshold_fix(random_list)
    print(random_items)
    real_no = 0
    for random_item in random_items:
        data_support = 0
        for c in clients:
            data_support += c.encrypt_DP(random_item)
        if data_support >= (min_support * length):
            real_no += 1
    if real_no >= 4:
        print(round(server.Y, 4))
        break
    else:
        server.Y += 0.1

final_frequent_itemset = {}
for candidate_frequent in server.candidate_frequent_itemset:
    final_support_data = 0
    # 临界项集处理
    if (candidate_frequent[1]/conf['no_models']) >= server.X and (candidate_frequent[1]/conf['no_models']) < server.Y:
        for c in clients:
            final_support_data += c.encrypt_HE(candidate_frequent[0], public_key)
        decrypted_support_data = private_key.decrypt(final_support_data)
        if decrypted_support_data >= (min_support*length):
            final_frequent_itemset[frozenset(candidate_frequent[0])] = decrypted_support_data
# 上界项集处理
    if (candidate_frequent[1]/conf['no_models']) >= server.Y:
        # print(candidate_frequent[0])
        candidate_lenth = len(candidate_frequent[0])
        for c in clients:
            final_support_data += c.encrypt_DP(candidate_frequent[0])
        # 修正
        if final_support_data < (min_support * length):
            print("okkkk")
            correct_support_data = 0
            if candidate_lenth == 1:
                for c in clients:
                    final_support_data += c.encrypt_DP(candidate_frequent[0])
            if candidate_lenth == 2:
                item = random.sample(candidate_frequent[0], 1)
                for c in clients:
                    correct_support_data += c.encrypt_DP(frozenset(item))
                final_support_data = (correct_support_data + (min_support * length))/2
            if candidate_lenth > 2:
                lista = list(itertools.combinations(candidate_frequent[0], candidate_lenth-1))
                random_lista = random.sample(lista, 1)
                for c in clients:
                    correct_support_data += c.encrypt_DP(frozenset(random_lista))
                final_support_data = (correct_support_data + (min_support * length))/2
        final_frequent_itemset[frozenset(candidate_frequent[0])] = final_support_data

# 下界项集处理
    if (candidate_frequent[1]/conf['no_models']) < server.X:
        # print(candidate_frequent[0])
        candidate_lenth = len(candidate_frequent[0])
        for c in clients:
            final_support_data += c.encrypt_DP(candidate_frequent[0])
        # 修正
        if final_support_data > (min_support * length):
           print("okkk")
           correct_support_data = 0
           for c_item in server.candidate_frequent_itemset:
               if len(c_item) == len(candidate_frequent[0])+1:
                   if candidate_frequent[0].issubset(frozenset(c_item[0])):
                       for c in clients:
                           correct_support_data += c.encrypt_DP(c_item[0])
                       final_support_data = (correct_support_data + (min_support * length))/2
                       print(final_support_data)
                       break
           if correct_support_data == 0:
               for c in clients:
                final_support_data += c.encrypt_DP(candidate_frequent[0])
           print(final_support_data)
           final_frequent_itemset[frozenset(candidate_frequent[0])] = final_support_data


Global_frequent_itemset = []
for final_frequent_item in final_frequent_itemset:
     if final_frequent_itemset[final_frequent_item] >= (min_support * length):
        Global_frequent_itemset.append(final_frequent_item)

end_time = time.time()
print("耗时: {:.2f}秒".format(end_time - start_time))

value_frequent_itemset = []
for candidate_frequent in server.candidate_frequent_itemset:
    value_support_data = 0
    for c in clients:
        value_support_data += c.value(candidate_frequent[0])
    if value_support_data >= (min_support * length):
        value_frequent_itemset.append(candidate_frequent[0])


print(Global_frequent_itemset)
print(value_frequent_itemset)

# 计算相似度
similarity = server.get_Jaccard(Global_frequent_itemset, value_frequent_itemset)
print(similarity)









