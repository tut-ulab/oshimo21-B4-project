#python count.py <Data_Directory_Path> <Output_Directory_Path>
#Data_Directoryからすべてのファイルを読み込み、各ユーザのTweetの単語の頻度を数えるプログラム
#Data_Directoryと同じようなディレクトリの構成でファイルに出力する

import sys
import os
import glob
import json
import re
import nltk
import time

#tweetから単語を数える
def TweetWordCount(tweet, CountWord):
    #WordList : List[str]
    #tweetに含まれる単語のList
    WordList = nltk.word_tokenize(tweet)
    #WordListに含まれる単語をひとつずつCountWordに加える
    for word in WordList:
        #単語をすべて小文字に変換
        word = str.lower(word)
        #すでに出現している単語かどうか確認
        #すでに出現している単語なら頻度を1増やす
        if (word in CountWord.keys()):
            temp = CountWord[word]
            CountWord[word] = temp + 1
        #まだ出現していない単語なら頻度を1にする
        else:
            CountWord[word] = 1


#コマンドライン引数の取得
argv = sys.argv

#実行の制限
if (len(argv) != 3):
    print("the number of input is wrong")
    print("please do input below")
    print("python count.py <Data_Directory_Path> <Output_Path>")
    sys.exit()
else:
    #DataPath : string
    #Dataの入っている複数のディレクトリが入っているディレクトリ
    #OutputPath : string
    #出力データを出すディレクトリ
    DataPath = argv[1]
    OutputPath = argv[2]

start = time.time()

#DataDirectory内のFileの集合の取得

#FileList : Iterator
#Data_Directoryの中のfile集合

FileList = glob.iglob(DataPath+"/**/*.txt", recursive=True)
FileCount = 0
#各FileからTextの語を数える

#id : str
#現在読みこんでいるTweetをしたユーザのid
id = ""
#UserList : List[str]
#読みこんだファイル群の中のユーザの集合
UserList = []
#CountWord : Dict{key:str, value:int}
#現在読みこんでいるファイルで数えた単語の数
CountWord = {}
#AllCountWord : Dict{key:str, value:int}
#すべてのファイルで数えた単語の数
AllCountWord = {}

#Path : string
#現在読みこんだ結果を出力するPath
Path = ""

#分かち書きの準備
nltk.download('punkt')

for source in FileList:
    FileCount = FileCount + 1
    #CountWordの初期化
    CountWord.clear()
    #idの取得
    id = re.search(r'[0-9]+.txt', source).group()[:-4]
    #idをUserListに加える
    if (id not in UserList):
        UserList.append(id)
    
    #ファイルを読み込み、各Tweetでの単語の出現頻度を数える
    with open(source, "r", encoding="utf-8") as f:
        #ファイルの各行を読み込む
        for line in f.readlines():
            #読み込むファイルの各行の構成は、id[tab]Tweet Objectとなっているので、Tweet オブジェクトを取り出す
            #Tweet Object : str
            #JSON形式
            #https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
            TweetObject = line.split("\t")[1]
            #tweet : str
            #tweetの内容
            #tweetの内容を受け取る
            tweet = json.loads(TweetObject)["full_text"]
            #tweet内の単語を数える
            #testData(tweet5回分について手で数えて、あっていることを確認した)
            TweetWordCount(tweet, CountWord)
    
    #Pathの作成
    Path = OutputPath + id[0:4] + "/" + id[4:8] + "/" + id[8:12] + "/" + id[12:16] + "/" + id + ".json"
    
    #ディレクトリの作成
    os.makedirs(Path[:-24], exist_ok=True)
    #ユーザのtweetについて、単語を数え上げた結果を、JSONファイルに出力する
    with open(Path, 'w') as f:
        json.dump(CountWord, f)
    
    #個々のユーザの単語の頻度をすべてのユーザの単語の頻度に加える
    for word, frec in CountWord.items():
        #もし含まれている単語なら頻度分追加
        if (word in AllCountWord.keys()):
            temp = AllCountWord[word]
            AllCountWord[word] = temp + frec
        #もし含まれていない単語なら単語ごと追加
        else:
            AllCountWord[word] = frec

print(FileCount)
#UserListとAllCountWordの出力
#UserList
with open(OutputPath+"UserList.txt", 'w') as f:
    for user in UserList:
        f.write(user+"\n")

#AllCountWord
with open(OutputPath+"AllCountWord.json", 'w') as f:
    json.dump(AllCountWord, f)

end = time.time()
print(end - start)
