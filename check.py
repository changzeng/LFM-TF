# encoding: utf-8

# author: liaochangzeng
# github: https://github.com/changzeng

with open("data.all") as fd:
    item_list = fd.read().strip().split("\n")
    item_list = [item.split(",") for item in item_list]
    user_num = max([int(item[0]) for item in item_list])
    item_num = max([int(item[1]) for item in item_list])

print(user_num, item_num)
