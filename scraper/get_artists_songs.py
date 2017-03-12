from bs4 import BeautifulSoup as bs
import urllib
import requests
import time
import nltk
from gensim import corpora
import sys
from song_lists import *



cache = "https://web.archive.org/web/"
url = "www.azlyrics.com"

j = 0
for i in mitski:
    lp_urls = []
    print(cache + url + i[1][2:])


#print(lp_urls)
