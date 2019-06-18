# import文
import MeCab as mc
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

# スクレイピングしたデータをデータベースに格納するための関数定義
conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./test.db")
    
# コネクションを断つ
def close():
    conn.close()

# 全レビューを取り出す関数を定義
def get_review():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT review FROM Reviews")
        res = cursor.fetchall()
        return res
    finally:
        close()

# 分かち書き
def mecab_analysis(texts):
    t = mc.Tagger("")
    t.parse('')
    output = []
    node =  t.parseToNode(texts)  
    while node:
        if node.surface != "":  # ヘッダとフッタを除外
            word_type = node.feature.split(",")[0]
            if word_type in ['名詞','動詞']:
                output.append(node.surface)
        node = node.next
        if node is None:
            break
    return output

# iつのタイトルを取り出す関数を定義
def id_from_title(title):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT id FROM Reviews WHERE title = ?",(title,))
        res = cursor.fetchone()
        return res
    finally:
        close()

def title_from_id(id):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT title FROM Reviews WHERE id = ?",(id,))
        res = cursor.fetchone()
        return res
    finally:
        close()

def Word2Vec(input_title):
    # 分かち書きしたリストのリストを作成
    wakati_all = []
    for review in get_review():
        wakati_all.append(mecab_analysis(review[0]))

    # ストップワーズ
    stop_words=["ストーリー","ストーリ","前半","後半","展開","シーン","用語","ちゃん","さん","op","ed","(",")","これ","こと","よう","一","的","評価","総合","ところ","の","作","回","視聴","それ","?)","さ","ここ","原作","設定","&","!","?","もの","作品","ん"]

    # dataには分かち書きをjoinで合わせたテキストを入力。doc_idsはdataと同じ長さ(1~3000)の整数が入る
    data = []
    doc_ids = []
    for wakati in wakati_all:
        delete_stop = [word for word in wakati if word not in stop_words]
        data.append(" ".join(delete_stop))

    doc_ids = [length+1 for length in range(len(data))]

    vectorizer = TfidfVectorizer(analyzer="word", max_df=0.9)
    vecs = vectorizer.fit_transform(data)

    sim = cosine_similarity(vecs)
    
    docs = zip(doc_ids,sim[id_from_title(input_title)[0]-1])
    for doc_ids,similarity in sorted(docs,key=lambda x: x[1], reverse = True)[:10]:
        title = title_from_id(doc_ids)[0]
        print(doc_ids,title,similarity)