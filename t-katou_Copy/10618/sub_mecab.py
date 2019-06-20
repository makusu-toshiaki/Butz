import MeCab as mc
import sqlite3
import mecab

conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./test.db")
    
# コネクションを断つ
def close():
    conn.close()

# テーブルを作成
def create_table_mecab():
    # DROP=消す.
    conn.execute("DROP TABLE IF EXISTS mecab")
    conn.execute("""CREATE TABLE mecab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            wakati TEXT
    )""")

# アニメタイトルと重要な単語を格納する関数を定義
def load_mecab(title,wakati):
    try:
        connect()
        conn.execute("INSERT INTO mecab (title,wakati) VALUES (?,?)", (title,wakati))
        conn.commit()
    finally:
        close()

review = mecab.get_review()
title = mecab.get_title()

wakati_all = [mecab.mecab_analysis(wakati[0]) for wakati in review]

try:
    connect()
    create_table_mecab()

    for i in range(3000):
        load_mecab(title[i][0], " ".join(wakati_all[i]))
finally:
    close()