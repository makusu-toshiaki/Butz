import requests
from bs4 import BeautifulSoup
import sqlite3

# スクレイピングしたデータをデータベースに格納するための関数定義
conn = None

# データベースに接続する
def connect():
    global conn
    conn = sqlite3.connect("./anime.db")
    
# コネクションを断つ
def close():
    conn.close()
    
# テーブル作成
def create_table_Url():
    # DROP=消す.
    conn.execute("DROP TABLE IF EXISTS Url")
    conn.execute("""CREATE TABLE Url (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT
    )""")

def load_Url(url):
    conn.execute("INSERT INTO Url (url) VALUES (?)", (url,))
    conn.commit()

# ページ移動、及びデータ格納のための関数を定義
def next_page(url,next_url,i):
    try:
        connect()
        r = requests.get(url+next_url)
        html_soup = BeautifulSoup(r.text, 'html.parser')
        new_url_all = [r["href"] for r in html_soup.find("td", class_ ="article container").find_all("a")]
        next_url = new_url_all[len(new_url_all)-1]
        if i != 0:
            del new_url_all[0:2]
            del new_url_all[len(new_url_all)-2:]
        else:
            del new_url_all[len(new_url_all)-1]
        for new_url in new_url_all:
            load_Url(new_url)
        return next_url
    finally:
        close()



# URL設定。アニメ評価新着順に設定
url = 'https://sakuhindb.com'
next_url = "/anime/anime.html"

# テーブルを作成し、30ページ文のアニメのを格納。1ページ100URLなので、全部で3000URL
try:
    connect()
    create_table_Url()
finally:
    close()

for i in range(30):
    next_url = next_page(url,next_url,i)