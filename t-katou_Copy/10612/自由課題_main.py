import sqlite3
import 自由課題_url_scraping
import 自由課題_review_scraping
import 自由課題_mecab

# スクレイピングしたデータをデータベースに格納するための関数定義
conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./test.db")
# コネクションを断つ
def close():
    conn.close()

def rate_from_title(title):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT rate FROM Reviews WHERE title = ?",(title,))
        res = cursor.fetchone()
        return res
    finally:
        close()

# 全ての重要単語を取り出す関数を定義
def get_all_word():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT text FROM TF_IDF")
        res = cursor.fetchall()
        return res
    finally:
        close()

# 指定したアニメの重要単語を取り出す関数を定義
def get_word_solo(title):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT text FROM TF_IDF WHERE title = ?",(title,))
        res = cursor.fetchone()
        return res
    finally:
        close()

# textからタイトルを取り出す
def title_from_word(word):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT title FROM TF_IDF WHERE text = ?",(word,))
        res = cursor.fetchone()
        return res
    finally:
        close()

print("プログラムを開始します")
if "n" == input("TF-IDFのデータベースはありますか？(y or n):"):
    if "n" == input("URLはありますか？(y or n):"):
        自由課題_url_scraping.scraping()
        自由課題_review_scraping.scraping()
        自由課題_mecab.TF_IDF()
    elif "n" == input("レビューはありますか？(y or n):"):
        自由課題_review_scraping.scraping()
        自由課題_mecab.TF_IDF()
    else:
        自由課題_mecab.TF_IDF()

title_input=input("タイトルを入力してください：")
f = float(input("評価の誤差を入力してください(小数点)："))
success = []
all_word = [other_word[0].split() for other_word in get_all_word()]

for other_word in all_word:
    for word in get_word_solo(title_input)[0].split():
        if word in other_word:
            if rate_from_title(title_input)[0]-f <= rate_from_title(title_from_word(" ".join(other_word))[0])[0] and rate_from_title(title_input)[0]+f >= rate_from_title(title_from_word(" ".join(other_word))[0])[0]:
                success.append(title_from_word(" ".join(other_word))[0])
                break

print(success)