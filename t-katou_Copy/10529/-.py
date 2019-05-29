#!/usr/bin/env python
# coding: utf-8

# In[283]:


from sklearn import ensemble
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import tree
import graphviz
import pandas as pd
import pandas_profiling
import pixiedust
import pivottablejs


# In[266]:


df = pd.read_csv('titanic.csv')


# In[225]:


pandas_profiling.ProfileReport(df)


# In[204]:


print(df.Age.mean())
df.Age.sort_values(ascending=False)


# In[205]:


print(df[df.Age > 100])
df.iloc[404]


# In[206]:


# 推測できそうな要素がなければ思い切って捨てる
df[df.Age > 100]


# In[234]:


df = df.drop(index=[404,605,788])


# In[209]:


df.Age.sort_values(ascending=True)


# In[235]:


df = df.drop(index=[666])


# In[236]:


df.Age.mean()


# In[212]:


df[df.Pclass.isna()]


# In[213]:


# Pclassごとに平均差があるか
pivottablejs.pivot_ui(df)


# In[153]:


df.iloc[36] = df.iloc[36].fillna({'Pclass': 2})


# In[267]:


for i in df[df.Pclass.isna()].index:
    if df.iloc[i].Fare < 17:
        df.iloc[i] = df.iloc[i].fillna({'Pclass':3})
    elif df.iloc[i].Fare < 73:
        df.iloc[i]= df.iloc[i].fillna({'Pclass':2})
    else:
        df.iloc[i] = df.iloc[i].fillna({'Pclass':1})


# In[268]:


df[df.Pclass.isna()].index


# In[272]:


df.Sex.unique()


# In[270]:


df.Sex = df.Sex.replace('man', 'male').replace('Woman', 'female').replace('women', 'female')


# In[271]:


df.iloc[108] = df.iloc[108].fillna({'Sex': 'female'})
df.iloc[370] = df.iloc[370].fillna({'Sex': 'female'})


# In[274]:


df.describe()


# In[279]:


df['Pclass'] = pd.get_dummies(df['Pclass'],drop_first=True)


# In[282]:


df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})


# In[285]:


X = df.drop(columns='Survived').drop(columns='Name')
Y = df['Survived']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=0.8)


# In[286]:


random_forest= ensemble.RandomForestClassifier(max_depth=5)
random_forest.fit(X_train, Y_train)
random_forest.score(X_test, Y_test)


# In[288]:


estimators = random_forest.estimators_
dot_data = tree.export_graphviz(estimators[0], # 決定木オブジェクトを一つ指定する
                                out_file=None, # ファイルは介さずにGraphvizにdot言語データを渡すのでNone
                                filled=True, # Trueにすると、分岐の際にどちらのノードに多く分類されたのか色で示してくれる
                                rounded=True, # Trueにすると、ノードの角を丸く描画する。
                                feature_names=df.columns.drop('Survived').drop('Name'), # これを指定しないとチャート上で特徴量の名前が表示されない
                                class_names='Survived', # これを指定しないとチャート上で分類名が表示されない
                                special_characters=True # 特殊文字を扱えるようにする
                                )
graph = graphviz.Source(dot_data)
graph.render("decision-tree", format="png")


# In[292]:


import requests
from bs4 import BeautifulSoup


# In[290]:


res = requests.get('https://qiita.com/matsu0228/items/edf7dbba9b0b0246ef8f')


# In[294]:


soup = BeautifulSoup(res.content, 'lxml')


# In[297]:


[i.text for i in soup.findAll('a', class_='it-Tags_item')]


# In[298]:


diamond = pd.read_csv('diamond.csv')


# In[299]:


diamond


# In[ ]:




