import pymysql.cursors
import os
from aws_creds import *
from analyze_lyrics import *

db_name = "main"
table = "songs"
connection = pymysql.connect(host=aws_endpoint,
                             user=aws_username,
                             password=aws_password,
                             db=db_name,
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
    # Create a new

try:
    cursor.execute("""DROP TABLE {};""".format(table))
    connection.commit()
except pymysql.err.InternalError:
    pass
sql =  """CREATE TABLE IF NOT EXISTS `songs`
(
    ID BIGINT,
    title VARCHAR( 200 ) NOT NULL,
    artist VARCHAR( 200 ) NOT NULL,
    lyrics TEXT,
    album TEXT,
    link TEXT,
    sentiment TEXT,
    PRIMARY KEY ( `ID` )
);"""

cursor.execute(sql)

artists = ['Mitski', 'LinkinPark', 'Beatles', 'TaylorSwift', 'TwentyOnePilots']

i = 0
for a in artists:
    path = 'Artists/' + a +'/lyrics/'
    for filename in os.listdir(path):
        if(filename == "urls.txt"):
            continue
        f = open(path + filename, "r")
        title = f.readline().rstrip()
        title = f.readline().rstrip()
        lyrics = f.read()
        if(title == ""):
            f.close()
            continue
        print(title)
        tup = (i, title.encode('utf-8'), a.encode('utf-8'), lyrics.encode('utf-8'), None, None, str(get_sentiment(a, filename)))
        #print(tup)
        cursor.execute("""INSERT INTO songs VALUES (%s, %s, %s, %s, %s, %s, %s)""", tup)
        #print(lyrics)
        f.close()
        i+= 1


connection.commit()
