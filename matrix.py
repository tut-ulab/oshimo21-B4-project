#python matrix.py <UserList> <UserVocab> <WordVocab> <CountDataDirectory> <OutputDirectory>

import enum
import time
import sys
import json
import numpy
import numpy.linalg
from scipy.linalg.special_matrices import convolution_matrix
from sklearn.decomposition import TruncatedSVD
import scipy.linalg
from scipy.sparse import csr_matrix, csc_matrix, coo_matrix, lil_matrix

argv = sys.argv
if (len(argv) != 6):
    print("the number of input is wrong")
    print("please do input below")
    print("python matrix.py <UserList> <UserVocab> <WordVocab> <CountDataDirectory> <OutputDirectory>")
    sys.exit()
else:
    OutputPath = argv[5]

#時間計測
start = time.time()

#UserList(全ユーザの読み込み)
#UserList : List
UserList = []

with open(argv[1], 'r') as f:
    for line in f.readlines():
        temp = line.rstrip()
        UserList.append(temp)

#UserVocab(ボキャブラリに含まれるユーザの読み込み)
#UserVocab : List
UserVocab = []

with open(argv[2], 'r') as f:
    for line in f.readlines():
        temp = line.rstrip()
        UserVocab.append(temp)

#WordVocab(ボキャブラリに含まれる単語の読み込み)
#WordVocab : List
WordVocab = []

with open(argv[3], 'r', encoding="utf-8") as f:
    for line in f.readlines():
        temp = line.rstrip()
        WordVocab.append(temp)


#ボキャブラリからカウントの行列を作成
#CountMatrix : numpy.matrix
#データが多いので動かない
#CountMatrix = numpy.zeros((len(UserVocab), len(WordVocab)))
#疎行列で実装　要素の変更を行うのでlil
CountMatrix = lil_matrix(coo_matrix((len(UserVocab), len(WordVocab))))

#各userからボキャブラリに含まれる単語を数える
for i, user in enumerate(UserVocab):
    #pathの作成
    path = user[0:4] + "/" + user[4:8] + "/" + user[8:12] + "/" + user[12:16] + "/" + user + ".json"
    #jsonファイルの読み込み
    with open(argv[4] + path, 'r') as f:
        temp = json.load(f)
        #ボキャブラリに含まれる単語の頻度を得る
        for j, word in enumerate(WordVocab):
            if (word in temp.keys()):
                CountMatrix[i, j] = temp[word]

#PPMI行列を作成
#Matrix : numpy.matrix
#Matrix = numpy.zeros((len(UserVocab), len(WordVocab)))
#疎行列　要素の変更を行うのでlil
Matrix = lil_matrix(coo_matrix((len(UserVocab), len(WordVocab))))

#(i, j) = max(#(word, context) * D / #(word) * #(context) - log2(k))
#k : int マジックナンバー
k = 1
temp1 = sum(sum(CountMatrix).T)[0, 0]
temp2 = sum(CountMatrix.T)
temp3 = sum(CountMatrix)

for i, user in enumerate(UserVocab):
    for j, word in enumerate(WordVocab):
        if(CountMatrix[i, j] != 0):
            temp = numpy.log2((CountMatrix[i, j] * temp1)/(temp2[0, i] * temp3[0, j]))
            Matrix[i, j] = max(temp - numpy.log2(k), 0)

#行列の構成時間
end1 = time.time()

#行列の特異値分解を行い、ユーザの特徴ベクトルと単語の意味ベクトルを得る
#M = W * C^T
#M = U * Sigma * V^T
#W = U * rootSigma, C = V * rootSigma
#d : int 特徴ベクトルの次元数　マジックナンバー
#UserMatrix : numpy.matrix
#WordMatrix : numpy.matrix
d = 200
tSVD = TruncatedSVD(n_components=d)
transformedM = tSVD.fit_transform(Matrix)
U_d = transformedM / tSVD.singular_values_
Sigma_d = tSVD.singular_values_
VT_d = tSVD.components_
rSigma_d = scipy.linalg.sqrtm(numpy.diag(Sigma_d))

UserMatrix = U_d @ rSigma_d
WordMatrix = VT_d.T @ rSigma_d

#ボキャブラリに含まれないユーザの特徴ベクトルを求めるために必要な単語の確率を求める
ProbWord = sum(CountMatrix)/sum(sum(CountMatrix).T)[0, 0]

UserVector = {}

for user in UserVocab:
    UserVector[user] = numpy.array(UserMatrix[UserVocab.index(user)][:])

end2 = time.time()

#事前に、ボキャブラリに含まれていないユーザの特徴ベクトルを求めるために必要な行列を求めておく
#M = U * Sigma * V^T
#User = U * rootSigma
#Word = (rootSigma * V^T)^T = V * rootSigma(Sigmaは対角行列なのでSigma^T = Sigma)
#M = User * Word^T
#求めたい特徴ベクトルuに対応するMの行mを用いてuを求める
#m = u * Word^T
#m' = Word * u' | Word^T * m' = Word^T * Word * u'
#u' = (Word^T * Word)^-1 * Word^T * m'
R = numpy.linalg.solve(numpy.dot(WordMatrix.T, WordMatrix), WordMatrix.T)

#すべてのユーザの特徴ベクトルを求める
for user in UserList:
    #ボキャブラリに含まれているユーザの特徴ベクトルはすでに求めている
    #ボキャブラリに含まれていないユーザの特徴ベクトルを求める
    if (user not in UserVocab):
        #pathの作成
        path = user[0:4] + "/" + user[4:8] + "/" + user[8:12] + "/" + user[12:16] + "/" + user + ".json"
        #jsonファイルの読み込み
        with open(argv[4] + path, 'r') as f:
            temp = json.load(f)
            count = numpy.array([0 for i in range(len(WordVocab))])
            #ユーザの単語のカウントからボキャブラリに含まれている単語のカウントを取り出す
            for i, word in enumerate(WordVocab):
                if(word in temp.keys()):
                    count[i] = temp[word]
        s = sum(count)
        #uに対応するMの行mについて求める
        m = numpy.array([0 for i in range(len(WordVocab))])
        #Mの要素は,max(log2{(#(w, c) * D) / (#(w) * #(c))} - log2 k , 0) --- #(w, c)---同時出現頻度, #(w), #(c)---出現頻度
        #上記の式より変形すると(log2の中のみ), log2{P(w, c) / (P(w) * P(c))}
        #求めたい単語が決まっているとき、log2{(ベクトルを求めたい単語での周辺語の確率)/(周辺語の確率)}となる
        #今回、中心語がユーザに、周辺語に単語が対応している
        if (s != 0):
            for i, word in enumerate(WordVocab):
                if (count[i] == 0 or ProbWord[0, i] == 0):
                    m[i] = 0
                else:
                    m[i] = max(numpy.log2((count[i]/s)/ProbWord[0, i]) - numpy.log2(k), 0)
        u = numpy.array(R @ m)
        #求めた結果を格納する
        UserVector[user] = u

end3 = time.time()

#UserVectorをjsonファイルとして保存する
#保存の都合上、numpy.arrayをlistに変換後、保存
with open(OutputPath+"User2Vec_timeTest.json", 'w') as f:
    temp = dict(map(lambda x : (x[0], x[1].tolist()), UserVector.items()))
    json.dump(temp, f)

#サンプル外のユーザについてもとめるためにかかる時間
end4 = time.time()

#行列の構成にかかる時間
print("行列の構成にかかる時間")
print(end1 - start)
#サンプル内のユーザのユーザベクトルを求めるためにかかる時間
print("サンプル内のユーザのユーザベクトルを求めるためにかかる時間")
print(end2 - end1)
#サンプル外のユーザのユーザベクトルを求めるためにかかる時間
print("サンプル外のユーザのユーザベクトルを求めるためにかかる時間サンプル外のユー")
print(end3 - end2)
#
print("保存時間")
print(end4 - end3)
