import sqlite3
import url_scraping
import review_scraping
import tfidf
import cosine

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

# 重要単語からタイトルを取り出す
def title_from_word(word):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT title FROM TF_IDF WHERE text = ?",(word,))
        res = cursor.fetchone()
        return res
    finally:
        close()

def make_decimal():
    try:
        decimal = float(input("評価の誤差を入力してください(小数)："))
        if decimal < 0:
            print("プラスの数値を入れてください：")
            return make_decimal()
        return decimal
    except:
        print("プラスの数値を入れてください：")
        return make_decimal()

def main():
    title_input = input("好きなアニメのタイトルを入力してください：")
    while cosine.id_from_title(title_input) == None:
        print("そのタイトルはデータベースにありません")
        title_input = input("好きなアニメのタイトルを入力してください：")

    # 誤差作成
    decimal = make_decimal()

    print()
    print("似ているアニメ")
    cosine.same(title_input)

    print()
    print("おすすめアニメ")
    success = []
    for other_word in get_all_word():
        for word in get_word_solo(title_input)[0].split():
            if word in other_word[0].split():
                if rate_from_title(title_input)[0]-decimal <= rate_from_title(title_from_word(other_word[0])[0])[0] and rate_from_title(title_input)[0]+decimal >= rate_from_title(title_from_word(other_word[0])[0])[0]:
                    success.append(title_from_word(other_word[0])[0])
                    break
    print(success)

    if "n" != input("続けますか？(y or n)："):
        main()


print("プログラムを開始します")

if "n" == input("TF-IDFのデータベースはありますか？(y or n):"):
        if "n" == input("URLはありますか？(y or n):"):
            url_scraping.scraping()
            review_scraping.scraping()
            review_scraping.mecab_start()
            tfidf.TF_IDF()
        elif "n" == input("レビューはありますか？(y or n):"):
            review_scraping.scraping()
            review_scraping.mecab_start()
            tfidf.TF_IDF()
        else:
            tfidf.TF_IDF()

main()