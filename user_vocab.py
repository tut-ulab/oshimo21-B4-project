#python user_vocab.py <UserList> <Output_Directory>
#UserListから基本となるユーザをランダムに選ぶ
import sys
import random

argv = sys.argv

#実行の制限
if(len(argv) != 3):
    print("the number of input is wrong")
    print("please do input below")
    print("python user_vocab.py <UserList> <Output_Directory>")
    sys.exit()
else:
    OutputPath = argv[2]


#選ぶユーザの数 : マジックナンバー
number = 10000

#UserList : List[str]
#すべてのユーザのリスト
UserList = []

with open(argv[1], 'r') as f:
    for line in f.readlines():
        #改行コードの削除
        temp = line.rstrip()
        #UserListに追加
        UserList.append(temp)

#UserVocab : List[str]
#UserListからnumberだけuserをランダムに取り出す
UserVocab = random.sample(UserList, number)

#UserVocabの出力
with open(OutputPath+"user_vocab4.txt", 'w') as f:
    for user in UserVocab:
        f.write(user+"\n")
