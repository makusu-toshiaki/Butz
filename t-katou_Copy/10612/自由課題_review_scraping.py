import requests
from bs4 import BeautifulSoup
import sqlite3
import oseti

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
def get_url():
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT url FROM Url")
        res = cursor.fetchall()
        return res
    finally:
        close()

# load_Reviewsの略。評判分析を行い、評価を出す。タイトル、レビュー、評価をデータベースに格納する関数を定義
def sub_load_Reviews(url,g_u):
    r = requests.get(url+g_u)
    res_soup = BeautifulSoup(r.content, 'html.parser')
    f_table = res_soup.find("td", class_="padding_cell").find_all("div", itemprop="reviewBody")
    text_all=""
    for text in f_table:
        text_all += text.text

    o = oseti.Analyzer()
    rate_all=[]
    for rate in o.analyze(text_all):
        if int(rate) != 0:
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

def scraping():
    url = 'https://sakuhindb.com'

    # テーブルを作成し、タイトル・レビュー・評価をデータベースに格納する
    try:
        connect()
        create_table_Reviews()
    finally:
        close()
    for g_u in get_url():
        sub_load_Reviews(url,g_u[0])