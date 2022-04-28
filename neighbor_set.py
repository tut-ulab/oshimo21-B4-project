#python neighbor_set.py <following.err> <followers.err> <AllUser> <following> <followers> <UserList> <OutputDirectory>
#<following.err> <followers.err> : following情報またはfollowers情報の取得に失敗したユーザについて書かれているファイル
#<AllUser> : following情報とfollowers情報の取得の試行を行ったユーザの情報ファイル
#<following> <followers> : following情報とfollowers情報
#<UserList> : tweet情報を取得したユーザ
#
import sys
import glob
import gzip
import random

argv = sys.argv

if(len(argv) != 8):
    print("the number of input is wrong")
    print("please do input below")
    print("python follow_ratio.py <following.err> <followers.err> <AllUser> <following> <followers> <UserList> <OutputDirectory>")
    sys.exit()

#following情報またはfollowers情報の取得に失敗したユーザ(失敗ユーザ)を取得する
FalseUser = {}

#following情報取得のエラー
with open(argv[1], "r") as f:
    for line in f.readlines():
        id = line.split("\t")[0]
        #初めての場合は登録
        if(id not in FalseUser.keys()):
            FalseUser[id] = 1
        #初めてでない場合は回数を増やす
        else:
            temp = FalseUser[id]
            FalseUser[id] = temp + 1

#followers情報取得のエラー
with open(argv[2], "r") as f:
    for line in f.readlines():
        id = line.split("\t")[0]
        #初めての場合は登録
        if (id not in FalseUser.keys()):
            FalseUser[id] = 1
        #初めてでない場合は回数を増やす
        else:
            temp = FalseUser[id]
            FalseUser[id] = temp + 1

#Followデータ取得を行った全ユーザの取得
#following情報、followers情報のどちらも取得できたユーザ(成功ユーザ)を取得する
SuccessUser = set()

with open(argv[3], 'r') as f:
    for line in f.readlines():
        id = line.rstrip()
        #もし失敗ユーザでないなら成功ユーザにする
        if(id not in FalseUser.keys()):
            SuccessUser.add(id)

EdgeSet = set()

#following情報の取得
FileList = glob.iglob(argv[4]+"*.txt.gz")

for file in FileList:
    with gzip.open(file, "rt") as f:
        for line in f.readlines():
            line = line.rstrip()
            #user1 → user2
            user1 = line.split(";")[0]
            user2 = line.split(";")[1]
            if ({user1} <= SuccessUser):
                EdgeSet.add((user1, user2))

#followers情報の取得
FileList = glob.iglob(argv[5]+"*.txt.gz")

for file in FileList:
    with gzip.open(file, "rt") as f:
        for line in f.readlines():
            line = line.rstrip()
            #user1 → user2
            user1 = line.split(";")[1]
            user2 = line.split(";")[0]
            if ({user1} <= SuccessUser):
                EdgeSet.add((user1, user2))

print("SuccessUser")
print(SuccessUser)
print("EdgeSet")
print(EdgeSet)

#VecUserSet　ベクトルを作成できたユーザの集合
VecUserSet = set()

with open(argv[6], "r") as f:
    for line in f.readlines():
        user = line.rstrip()
        VecUserSet.add(user)

print("VecUserSet")
print(VecUserSet)

#UserList ベクトルを作成できて、なおかつFollow情報の取得に成功したユーザのリスト
UserList = []
for temp in SuccessUser & VecUserSet:
    UserList.append(temp)

#隣接しているユーザの決定
PairSet = set()

#隣接しているユーザの取得
def NeighborUsers(user, UserList, EdgeSet):
    NeighborList = []
    for temp in UserList:
        if(temp != user):
            if({(user, temp)} <= EdgeSet or {(temp, user)} <= EdgeSet):
                NeighborList.append(temp)
    return NeighborList

#ユーザをひとり選ぶ
#隣接ユーザを取得
#隣接しているユーザの中からペアの相手を決定
#すでに決めたペアでないか調べる

count = 0
#隣接ユーザのある可能性のあるユーザ
tempList = UserList

while(count < 1000):
    print(tempList)
    user1 = random.choice(tempList)
    neighbor = NeighborUsers(user1, tempList, EdgeSet)
    if(len(neighbor) == 0):
        if(user1 in tempList):
            tempList.remove(user1)
        continue
    else:
        user2 = random.choice(neighbor)
        if (user2 < user1):
            temp = user1
            user1 = user2
            user2 = temp
        if ({(user1, user2)} <= PairSet):
            continue
        else:
            PairSet.add((user1, user2))
            count += 1

print("PairSet")
print(PairSet)

with open(argv[7]+"neighbor_set.txt", "w") as f:
    for temp1, temp2 in PairSet:
        f.write(temp1+";"+temp2+"\n")
