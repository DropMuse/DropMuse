from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from bs4 import BeautifulSoup as bs, SoupStrainer
from bs4 import Comment
import time
from urllib import urlopen


def get_sentiment(song):
    scores = dict([('pos', 0), ('neu', 0), ('neg', 0), ('compound', 0)])

    if not song:
        return scores

    raw_text = song
    raw_text = re.sub("\n", ". ", str(raw_text))

    # Using already trained
    sid = SentimentIntensityAnalyzer()
    sentences = tokenize.sent_tokenize(raw_text)

    scores = dict([('pos', 0), ('neu', 0), ('neg', 0), ('compound', 0)])
    for sentence in sentences:

        ss = sid.polarity_scores(sentence)

        for k in sorted(ss):
            scores[k] += ss[k]

    return scores


def format_artist(artist):
    artist = artist.lower()
    if artist[0:2] == "a ":
        artist = artist.replace("a ", "", 1)
    elif artist[0:4] == "the ":
        artist = artist.replace("the ", "", 1)
    artist = artist.replace(" ", "", 1)
    artist = re.sub('[^0-9a-zA-Z]+', '', artist)
    return artist


def format_song(song):
    song = song.lower()
    song = song.replace(" ", "", 1)
    song = re.sub('[^0-9a-zA-Z]+', '', song)
    return song


def get_lyrics_with_urls(urls):
    # TODO

    ret = []
    for url in urls:
        time.sleep(3)
        print(url)

        response = urlopen(url, timeout=5)
        content = response.read()
        for lyrics in bs(content, "html.parser", parse_only=SoupStrainer('p')):
            if(lyrics.has_attr('style')):
                lyrics = re.sub('</?br/?>', '\n', str(lyrics))
                lyrics = re.sub('<.*?>', '', str(lyrics))
                lyrics = re.sub('\n', ' \n', str(lyrics))
                ret.append(lyrics)
                print(lyrics)
                print(str(get_sentiment(lyrics)))
    return ret

LYRICS_URL = '''
https://web.archive.org/web/20161007001058/http://www.azlyrics.com/lyrics/{}/{}.html
'''


def get_lyrics(artist, song):
    artist = format_artist(artist)
    song = format_song(song)

    time.sleep(1)
    url = LYRICS_URL.format(artist, song)
    content = None
    try:
        response = urlopen(url)
        content = response.read()
    except Exception as e:
        print(url)
        print(e)
        print("failed\n")
        return None

    soup = bs(content, "html.parser", parse_only=SoupStrainer('div'))
    for l in soup:
        for lyrics in soup.find_all(string=lambda t: isinstance(t, Comment)):
            if "start of lyrics" in lyrics or "Usage" in lyrics:
                lyrics = re.sub('</?br/?>', '', str(lyrics.parent))
                lyrics = re.sub('<.*?>', '', str(lyrics))

                return str(lyrics)
