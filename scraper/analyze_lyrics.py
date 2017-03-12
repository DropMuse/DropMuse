import nltk
from gensim import corpora
from bs4 import BeautifulSoup
from nltk import word_tokenize, tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import names
from nltk.sentiment.util import *
import os
import sys

if(len(sys.argv) == 0):
    print("Select an artist")
    exit()

def get_sentiment(artist, filename):

    path = 'Artists/' + artist +'/lyrics/'
    f = open(path + filename, "r")
    raw_text = f.read()
    stop_words = list(stopwords.words('english'))
    #print("Stop words {}\n\n\n\n".format(stop_words))
    # Tokenizing the words
    tokens = word_tokenize(raw_text)
    #print("{} tokens identified".format(len(tokens)))
    # Removing stop words from tokenized list
    tokens_without_stop_words = [t for t in tokens if t not in stop_words]
    #print("{} real tokens: \n\n\n\n\n{}".format(len(tokens_without_stop_words), tokens_without_stop_words))

    #Using already trained
    sid = SentimentIntensityAnalyzer()
    sentences = tokenize.sent_tokenize(raw_text)
    scores = dict([ ('pos', 0), ('neu', 0), ('neg', 0), ('compound',0)])
    for sentence in sentences:
        #print(sentence)
        ss = sid.polarity_scores(sentence)
        for k in sorted(ss):
            #print('{0}: {1}, '.format(k, ss[k]))
            scores[k]+=ss[k]
        #print(filename + ":\n" +
        #'pos : '+ str(scores['pos']) + '   neg : ' + str(scores['neg']) + '   neu : ' + str(scores['neu']) +
        #'   compound : ' + str(scores['compound']))
    f.close()
    return scores
