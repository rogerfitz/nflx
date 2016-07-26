
# coding: utf-8

# In[1]:

#Run with python3

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import datetime
import os
import string
import re


# In[2]:

def fetch(url):
    req=Request(url, headers={'User-Agent': 'Misc Robot'})
    html_week = urlopen(req).read()
    soup = BeautifulSoup(html_week, 'html.parser')
    return soup
        
def get_num(text):
    return re.findall(r"[0-9]*[0-9]", text)[0]


# In[3]:

class Catalog:
    def __init__(self):
        self.base_url='http://usa.newonnetflix.info/catalog/a2z/comedies'
        self.pages=['']+list(string.ascii_lowercase)
        self.object_urls=[]
        
    def fetch_all(self):
        for page in self.pages:
            url=self.base_url+'/'+page
            print(url)
            soup = fetch(url)
            self.parse(soup)
        print(len(self.object_urls))
            
    def parse_film_number(self, soup):
        total=soup.find('section').find_all('em')[0].text
        return get_num(total)

    def parse_category_number(self, soup):
        total=soup.find('section').find_all('em')[1].text
        return get_num(total)
    
    def parse(self, soup):
        self.num_objects=self.parse_category_number(soup)
        articles=soup.find_all('section')[3].find_all('article')
        for article in articles:
            self.object_urls.append(article.find_all('a')[1]['href'])       
        
    def __repr__(self):
        return self.base_url


# In[ ]:

netflix=Catalog()
netflix.fetch_all()


# In[ ]:

class Article():
    def __init__(self, url):
        self.url='http://usa.newonnetflix.info'+url
        self.build()
    
    def build(self):
        soup=fetch(self.url)
        self.parse(soup)
        return self.attrs
    
    def parse(self, soup):
        article=soup.find_all('article')[0]
        attrs={}
        attrs['img_src']=article.find_all('img')[0]['src']
        attrs['genre']=article.select('div[class=genre]')[0].text
        
        p=article.find_all('p')

        
        for i in range(0,len(p)):
            if p[i].find('strong'):


                attr=p[i].find('strong').text[:-1]
                if attr not in ['IMDB', 'IMDB Rating', 'Netflix Rating', 'Description']:
                    try:
                        val=p[i].text.split(': ')[1]
                    except:
                        print(attr, self.url)
                elif attr=='Description':
                    val=p[i+1].text

                elif attr=='IMDB':
                    attr='imdb_url'
                    val=p[i].find('a')['href']

                elif attr in ['Netflix Rating', 'IMDB Rating']:
                    try:
                        val=p[i].find_all('img')[-1]['title'].split(' ')[2]
                    except:
                        print(attr, self.url)

                attrs[attr.lower()]=val
                
        self.attrs=attrs


# In[ ]:

def build(url):
    soup=fetch('http://usa.newonnetflix.info'+url)
    return parse(soup)

def parse(soup):
    article=soup.find_all('article')[0]
    attrs={}
    attrs['img_src']=article.find_all('img')[0]['src']
    attrs['genre']=article.select('div[class=genre]')[0].text

    p=article.find_all('p')


    for i in range(0,len(p)):
        if p[i].find('strong'):


            attr=p[i].find('strong').text[:-1]
            if attr not in ['IMDB', 'IMDB Rating', 'Netflix Rating', 'Description']:
                try:
                    val=p[i].text.split(': ')[1]
                except:
                    print(attr)
            elif attr=='Description':
                val=p[i+1].text

            elif attr=='IMDB':
                attr='imdb_url'
                val=p[i].find('a')['href']

            elif attr in ['Netflix Rating', 'IMDB Rating']:
                try:
                    val=p[i].find_all('img')[-1]['title'].split(' ')[2]
                except:
                    print(attr)

            attrs[attr.lower()]=val
    return attrs



entries=[]
for idx, url in enumerate(netflix.object_urls):
    entries.append(Article(url).build())
    if idx%50==0:
        print(idx,len(netflix.object_urls))



# In[244]:

import pandas as pd


# In[258]:

media=pd.DataFrame.from_records(entries)
media=media[['cast',
       'certificate', 'date added', 'description', 'director', 'duration',
       'episode length', 'genre',  'imdb rating', 'imdb_url',
       'img_src', 'netflix rating','year']]

media.to_csv('media.csv')

