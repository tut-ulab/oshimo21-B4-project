#python similarity_test.py <User2Vec.json> <neighbor_set> <not_neighbor_set>
#<User2Vec.json> 特徴ベクトルを保存したjson形式のファイル
#<neighbor_set> 隣接しているユーザのペアの集合
#<not_neighbor_set> 隣接していないユーザのペアの集合

import sys
import json
import numpy
import statistics

argv = sys.argv

if(len(argv) != 4):
    print("the number of input is wrong")
    print("please do input below")
    print("python similarity_test.py <User2Vec.json> <neighbor_set> <not_neighbor_set>")
    sys.exit()

User2Vec = {}

#特徴ベクトルの読み込み
with open(argv[1], "r") as f:
    User2Vec = json.load(f)

#特徴ベクトルをnumpy.arrayに変換
User2Vec = dict(map(lambda x: (x[0], numpy.array(x[1])), User2Vec.items()))

#vec1とvec2のcosSimilarityを求める関数
def cosSim(vec1, vec2):
    result = 0
    temp1 = numpy.dot(vec1, vec2)
    temp2 = numpy.linalg.norm(vec1, ord=2) * numpy.linalg.norm(vec2, ord=2)
    if(temp1 != 0):
        result = temp1/temp2
    else:
        result = 0
    return result

#隣接しているユーザのペアの集合の読み込み
neighbor_pairs = []

with open(argv[2], "r") as f:
    for line in f.readlines():
        line = line.rstrip()
        user1 = line.split(";")[0]
        user2 = line.split(";")[1]
        neighbor_pairs.append((user1, user2))

neighbor_cosSim = [0 for i in range(len(neighbor_pairs))]

for i, pair in enumerate(neighbor_pairs):
    user1 = pair[0]
    user2 = pair[1]
    temp = cosSim(User2Vec[user1], User2Vec[user2])
    neighbor_cosSim[i] = temp

#隣接していないユーザのペアの集合の読み込み
not_neighbor_pairs = []

with open(argv[3], "r") as f:
    for line in f.readlines():
        line = line.rstrip()
        user1 = line.split(";")[0]
        user2 = line.split(";")[1]
        not_neighbor_pairs.append((user1, user2))

not_neighbor_cosSim = [0 for i in range(len(not_neighbor_pairs))]

for i, pair in enumerate(not_neighbor_pairs):
    user1 = pair[0]
    user2 = pair[1]
    temp = cosSim(User2Vec[user1], User2Vec[user2])
    not_neighbor_cosSim[i] = temp

print("neighbor_set median")
print(statistics.median(neighbor_cosSim))
print("neighbor_set mean")
print(statistics.mean(neighbor_cosSim))

print("not_neighbor_set median")
print(statistics.median(not_neighbor_cosSim))
print("not_neighbor_set mean")
print(statistics.mean(not_neighbor_cosSim))
