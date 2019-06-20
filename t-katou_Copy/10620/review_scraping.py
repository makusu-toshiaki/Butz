import requests
from bs4 import BeautifulSoup
import sqlite3
import oseti
from joblib import Parallel,delayed

# スクレイピングしたデータをデータベースに格納するための関数定義
conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./test.db")
    
# コネクションを断つ
def close():
    conn.close()

def create_table_Reviews():
    # DROP=消す.
    conn.execute("DROP TABLE IF EXISTS Reviews")
    conn.execute("""CREATE TABLE Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            review TEXT,
            rate FLOAT
    )""")

def load_Reviews(title, review, rate):
    conn.execute("INSERT INTO Reviews (title,review,rate) VALUES (?,?,?)", (title,review,rate))
    conn.commit()

# データベースに格納されているURLを取り出す関数を定義
def get_url_all():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT url FROM Url")
        res = cursor.fetchall()
        return res
    finally:
        close()

# 評判分析を行い、評価を出す。タイトル、レビュー、評価をデータベースに格納する関数を定義
def sub_load_Reviews(url,get_url):
    r = requests.get(url+get_url)
    res_soup = BeautifulSoup(r.content, 'html.parser')
    f_table = res_soup.find("td", class_="padding_cell").find_all("div", itemprop="reviewBody")
    text_all=""
    for text in f_table:
        text_all += text.text

    o = oseti.Analyzer()
    rate_all=[]
    for rate in o.analyze(text_all):
        if rate != 0:
            rate_all.append(rate)
    
    if len(rate_all)==0:
        rate = 0.0
    else:
        rate=sum(rate_all)/len(rate_all)
    title = res_soup.find("span", itemprop="name").text
    try:
        connect()
        load_Reviews(title, text_all, rate)
    finally:
        close()

def request(url):
    r = requests.get(url)
    res_soup = BeautifulSoup(r.content, 'html.parser')
    table = res_soup.find("td", class_="padding_cell").find_all("div", itemprop="reviewBody")

    text_all=""
    for text in table:
        text_all += text.text
    title = res_soup.find("span", itemprop="name").text

    return [title,text_all]

def get_rate(title,text):
    o = oseti.Analyzer()
    rate_all=[rate for rate in o.analyze(text_all) if rate != 0]
    
    if len(rate_all)==0:
        rate = 0.0
    else:
        rate=sum(rate_all)/len(rate_all)
        
    try:
        connect()
        load_Reviews(title, text_all, rate)
    finally:
        close()

def scraping():
    print("レビューのスクレイピング開始")

    # テーブルを作成し、タイトル・レビュー・評価をデータベースに格納する
    try:
        connect()
        create_table_Reviews()
    finally:
        close()
    
    url_all = ['https://sakuhindb.com'+url[0] for url in get_url_all()]
    # titleとレビュー
    title_text = Parallel(n_jobs=3)([delayed(request)(url) for url in url_all])
    Parallel(n_jobs=3)([delayed(get_rate)(tt[0],tt[1]) for tt in title_text])

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

def mecab_start():
    review = tfidf.get_review()
    title = tfidf.get_title()

    wakati_all = [mecab_analysis(wakati[0]) for wakati in review]

    try:
        connect()
        create_table_mecab()

        for i in range(3000):
            load_mecab(title[i][0], " ".join(wakati_all[i]))
    finally:
        close()