from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3

conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./test.db")
    
# コネクションを断つ
def close():
    conn.close()

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

# 全レビューの分かち書きされたリストを取り出す
def get_mecab():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT wakati FROM mecab")
        res = cursor.fetchall()
        return res
    finally:
        close()

def TF_IDF():
    print("TF-IDFの計算開始")
    # ストップワーズ
    stop_words=["ストーリー","描写","_","ーー","番組","ストーリ","前半","後半","展開","シーン","用語","ちゃん","さん","op","ed","(",")","これ","こと","よう","一","的","評価","総合","ところ","の","作","回","視聴","それ","?)","さ","ここ","原作","設定","&","!","?","もの","作品","ん"]

    # dataには分かち書きをjoinで合わせたテキストを入力。doc_idsはdataと同じ長さ(1~3000)の整数が入る
    data = [review[0] for review in get_mecab()]
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
        for w_id, tfidf in sorted(enumerate(vec), key=lambda x: x[1],reverse=True):
            lemma = vectorizer.get_feature_names()[w_id]
            if lemma not in stop_words:
                text.append(lemma)
            if len(text) >= 10:
                break
        load_TF_IDF(title[0]," ".join(text))