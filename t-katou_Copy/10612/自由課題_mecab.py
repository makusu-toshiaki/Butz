import MeCab as mc
from sklearn.feature_extraction.text import TfidfVectorizer

# TF_IDFに関わる関数を定義
# テーブルを作成
def create_table_TF_IDF():
    # DROP=消す.
    conn.execute("DROP TABLE IF EXISTS TF_IDF")
    conn.execute("""CREATE TABLE TF_IDF (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            text TEXT
    )""")

# アニメタイトルと重要な単語を格納する関数を定義
def load_TF_IDF(title,text):
    try:
        connect()
        conn.execute("INSERT INTO TF_IDF (title,text) VALUES (?,?)", (title,text))
        conn.commit()
    finally:
        close()

# 全タイトルを取り出す関数を定義
def get_title():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT title FROM Reviews")
        res = cursor.fetchall()
        return res
    finally:
        close()

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

# 指定したアニメのレビューを取り出す関数を定義
def get_review_solo(title):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT review FROM Reviews WHERE title = ?",(title,))
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
            if word_type in ['名詞']:
                output.append(node.surface)
        node = node.next
        if node is None:
            break
    return output

# 分かち書きしたリストのリストを作成
wakati_all = []
for review in get_review():
    wakati_all.append(mecab_analysis(review[0]))

# ストップワーズ
stop_words=["(",")","これ","こと","よう","一","的","評価","総合","ところ","の","作","回","視聴","それ","?)","さ","ここ","&","!","?","もの","作品","ん"]

# dataには分かち書きをjoinで合わせたテキストを入力。doc_idsはdataと同じ長さ(1~3000)の整数が入る
data = []
doc_ids = []
for wakati in wakati_all:
    delete_stop = [word for word in wakati if word not in stop_words]
    data.append(" ".join(delete_stop))

doc_ids = [length+1 for length in range(len(data))]

vectorizer = TfidfVectorizer(analyzer="word", max_df = 0.9)
vecs = vectorizer.fit_transform(data)

# TF-IDFテーブルを作成
try:
    connect()
    create_table_TF_IDF()
finally:
    close()

for doc_id, vec, title in zip(doc_ids, vecs.toarray(),get_title()):
    text = []
    for w_id, tfidf in sorted(enumerate(vec), key=lambda x: x[1],reverse=True)[:10]:
        lemma = vectorizer.get_feature_names()[w_id]
        text.append(lemma)
    load_TF_IDF(title[0]," ".join(text))