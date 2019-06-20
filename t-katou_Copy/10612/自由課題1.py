#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import文
import MeCab as mc
import requests
from bs4 import BeautifulSoup
import sqlite3
import oseti
from sklearn.feature_extraction.text import TfidfVectorizer


# In[100]:


# 評判分析をoでできるようにする
o = oseti.Analyzer()


# In[4]:


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

def create_table_Reviews():
    # DROP=消す.
    conn.execute("DROP TABLE IF EXISTS Reviews")
    conn.execute("""CREATE TABLE Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            review TEXT,
            rate FLOAT
    )""")
    
def load_Url(url):
    conn.execute("INSERT INTO Url (url) VALUES (?)", (url,))
    conn.commit()
    
def load_Reviews(title, review, rate):
    conn.execute("INSERT INTO Reviews (title,review,rate) VALUES (?,?,?)", (title,review,rate))
    conn.commit()


# In[ ]:


# URL設定。アニメ評価新着順に設定
url = 'https://sakuhindb.com'
next_url = "/anime/anime.html"


# In[111]:


# テーブルを作成し、30ページ文のアニメのを格納。1ページ100URLなので、全部で3000URL
try:
    connect()
    create_table_Url()
finally:
    close()

for i in range(30):
    next_url = next_page(url,next_url,i)
    print(str(i+1)+"回目")


# In[29]:


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


# In[39]:


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


# In[137]:


# load_Reviewsの略。評判分析を行い、評価を出す。タイトル、レビュー、評価をデータベースに格納する関数を定義
def l_R(url,g_u):
    r = requests.get(url+g_u)
    res_soup = BeautifulSoup(r.content, 'html.parser')
    f_table = res_soup.find("td", class_="padding_cell").find_all("div", itemprop="reviewBody")
    text_all=""
    for text in f_table:
        text_all += text.text

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


# In[138]:


# テーブルを作成し、タイトル・レビュー・評価をデータベースに格納する
try:
    connect()
    create_table_Reviews()
finally:
    close()
for g_u in get_url():
    l_R(url,g_u[0])


# In[11]:


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


# In[21]:


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


# In[9]:


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


# In[43]:


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


# In[12]:


wakati = []
for s in get_review():
    wakati.append(mecab_analysis(s[0]))


# In[13]:


# ストップワーズ
stop_words=["(",")","これ","こと","よう","一","的","評価","総合","ところ","の","作","回","視聴","それ","?)","さ","ここ","&","!","?","もの","作品","ん"]


# In[14]:


# dataには分かち書きをjoinで合わせたテキストを入力。doc_idsはdataと同じ長さ(1~3000)の整数が入る
data = []
doc_ids = []
stop = []
for w in wakati:
    stop = [a for a in w if a not in stop_words]
    data.append(" ".join(stop))

doc_ids = [length+1 for length in range(len(data))]


# In[18]:


vectorizer = TfidfVectorizer(analyzer="word", max_df = 0.9)
vecs = vectorizer.fit_transform(data)


# In[2]:


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
    
def load_TF_IDF(title,text):
    try:
        connect()
        conn.execute("INSERT INTO TF_IDF (title,text) VALUES (?,?)", (title,text))
        conn.commit()
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
        
def rate_from_title(title):
    try:
        connect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT rate FROM Reviews WHERE title = ?",(title,))
        res = cursor.fetchone()
        return res
    finally:
        close()


# In[90]:


try:
    connect()
    create_table_TF_IDF()
finally:
    close()


# In[91]:


for doc_id, vec, title in zip(doc_ids, vecs.toarray(),get_title()):
#     print(doc_id, title[0])
    text = []
    for w_id, tfidf in sorted(enumerate(vec), key=lambda x: x[1],reverse=True)[:10]:
        lemma = vectorizer.get_feature_names()[w_id]
#         print("\t{0:s}: {1:f}".format(lemma, tfidf))
        text.append(lemma)
    load_TF_IDF(title[0]," ".join(text))


# In[14]:


title_input=input("タイトルを入力してください：")

all_word = [other_word[0].split() for other_word in get_all_word()]
f = float(input("評価の誤差を入力してください(小数点)："))
success = []
for other_word in all_word:
    for word in get_word_solo(title_input)[0].split():
        if word in other_word:
            if rate_from_title(title_input)[0]-f <= rate_from_title(title_from_word(" ".join(other_word))[0])[0] and rate_from_title(title_input)[0]+f >= rate_from_title(title_from_word(" ".join(other_word))[0])[0]:
                success.append(title_from_word(" ".join(other_word))[0])
                break

print(success)

