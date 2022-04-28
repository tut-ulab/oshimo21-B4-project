#python word_vocab.py <AllCountWord> <Output_Directory>
#AllCountWordから上位n単語のvocabを作成

import sys
import json
import nltk

nltk.download('averaged_perceptron_tagger')

argv = sys.argv

#実行の制限
if(len(argv) != 3):
    print("the number of input is wrong")
    print("please do input below")
    print("python user_vocab.py <AllCountWord> <Output_Directory>")
    sys.exit()
else:
    OutputPath = argv[2]

AllCountWord = {}

#n : int シークレットナンバー
n = 10000

#jsonファイルの読み込み
with open(argv[1], 'r') as f:
    AllCountWord = json.load(f)

#総単語数
print("総単語数")
print(len(AllCountWord.keys()))

#WordVocab : List[str]
#AllCountWordから出現頻度上位n単語きりだす
WordVocab = []
countAll = 0
count = 0

for word ,freq in sorted(AllCountWord.items(), reverse=True, key=lambda x:x[1]):
    #nltkを用いた品詞の判定
    #名詞、代名詞
    #NN, NNS, NNP, NNPS, PRP, PRP$
    #動詞、補助動詞
    #VB, VBD, VBG, VBN, VBP, VBZ
    #形容詞・副詞
    #JJ, JJR, JJS, RB, RBR, RBS
    temp = nltk.pos_tag([word])
    judge = (temp[0][1] == 'JJ') | (temp[0][1] == 'JJR') | (temp[0][1] == 'JJS') | (temp[0][1] == 'RB') | (temp[0][1] == 'RBR') | (temp[0][1] == 'RBS')  
    if(judge):
        countAll += 1
        if(count < n):
            WordVocab.append(word)
            count += 1

print("対象の単語数")
print(countAll)

#ファイルに出力
with open(OutputPath+"word_vocab_adjective_test.txt", 'w', encoding="utf-8") as f:
    for word in WordVocab:
        f.write(word+"\n")
