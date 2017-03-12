from bs4 import BeautifulSoup as bs
from bs4 import Comment
import urllib
import requests
import time
import nltk
from gensim import corpora
from lxml.html import fromstring
import lxml.html as PARSER
import os
import re
import sys


if(len(sys.argv) == 0):
    print("Select an artist")
    exit()
#artist = sys.argv[1]
#response = urllib.request.urlopen(path + 'acrosstheline.html').read()


artists = ['Mitski', 'LinkinPark', 'Beatles', 'TaylorSwift', 'TwentyOnePilots']

for artist in artists:
    path = 'Artists/' + artist +'/urls/'
    for filename in os.listdir(path):
        print(filename)
        if(filename=='urls.txt'):
            continue
        f = open(path + "../lyrics/" + filename.rstrip('.html') + ".txt", "w")


        soup = bs(open(path + filename), "lxml")
        title = soup.find_all('b', class_=False)
        if len(title) == 0:
            continue
        f.write(artist + "\n")
        f.write(re.sub('<.*?>|"', '', str(title[len(title) - 1])))

        for lyrics in soup.find_all(string=lambda text:isinstance(text,Comment)):
            if "start of lyrics" in lyrics or "Usage" in lyrics:
                curr = re.sub('<.*?>|([^\s\w]|_)', '', str(lyrics.parent))
                f.write(curr)

                break
        f.close()
        print("====================================")
