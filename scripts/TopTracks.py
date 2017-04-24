import spotipy
import sys
import json
import pymysql.cursors
import os
import codecs

def Scraper(name):

	spotify = spotipy.Spotify()

	#text_file = open("Artists.txt", "r")											#txt file containing artists, 1 per line
	#Artists = text_file.readlines()
	#text_file.close()

																					#change the above to argv[1] later, where argv[1] is an artist name
	connection = pymysql.connect(host='dropmusedb.cy9tsxymeyxa.us-west-2.rds.amazonaws.com',
								 port=3306,
	                             user='dropmuse',
	                             password='uiuc2019!',
	                             db='main',
	                             cursorclass=pymysql.cursors.DictCursor)
	cursor = connection.cursor()

	try:
	    # cursor.execute("""DROP TABLE songs;""")
	    connection.commit()
	except pymysql.err.InternalError:
	    pass

	sql = """CREATE TABLE IF NOT EXISTS `songs`
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

	###Actual Method Below###
	#print('# of artists in the text file: ' + str(len(Artists)))
	#print()
	print()

	#for i in range(0, len(Artists)):
	if(name == None):
		return 10
#for name in Artists:															#name is the Artist Name
	print('Artist: ' + name)
	ArtistInfo = spotify.search(q='artist:' + name, type='artist')
	if(ArtistInfo['artists']['total'] == 0):
		print('\nInvalid Artist Entered. \nPlease Correct Your Spelling or Choose Another Artist')
		return 11
	print('ArtistID: ' + ArtistInfo['artists']['items'][0]['id'])
	ArtistID = ArtistInfo['artists']['items'][0]['id']							#ArtistID
	AName = ArtistInfo['artists']['items'][0]['name']							#Correct Artist Name - Spotify's name, not typed in name
	#print(len(ArtistInfo['artists']['items']))

	#Albums = spotify.artist_albums(ArtistID, album_type='single,album', limit='50')

	TopInfo = spotify.artist_top_tracks(ArtistID)
	#print(len(TopInfo['tracks']))
	#for each in range(0, len(TopInfo['tracks'])):
	for each in range(0, 4):
		#print(AName)
		#print(TopInfo['tracks'][each]['album']['name'])
		#print(TopInfo['tracks'][each]['id'])
		#print(TopInfo['tracks'][each]['name'])
		#if(TopInfo['tracks'][each]['preview_url'] != None):
		#	print('Preview URL: ' + TopInfo['tracks'][each]['preview_url'])							#Preview URL
		#print(TopInfo['tracks'][each]['duration_ms'])
		#print()

		tup = (TopInfo['tracks'][each]['name'].encode('utf-8'), AName.encode('utf-8'), TopInfo['tracks'][each]['album']['name'].encode('utf-8'),
					TopInfo['tracks'][each]['preview_url'], TopInfo['tracks'][each]['id'], TopInfo['tracks'][each]['duration_ms']/1000);
		cursor.execute("INSERT INTO songs(title, artist, album, preview_url, spotify_id, duration) "
                   "VALUES (%s, %s, %s, %s, %s, %s)", tup)					 
		#oldTup = (TopInfo['tracks'][each]['id'], AName.encode('utf-8'), TopInfo['tracks'][each]['album']['name'].encode('utf-8'), 
		#			TopInfo['tracks'][each]['name'].encode('utf-8'), TopInfo['tracks'][each]['preview_url'], TopInfo['tracks'][each]['duration_ms']/1000);
		#cursor.execute("INSERT INTO songs_dev(spotify_id, artist, album, song, song_url, duration) "
        #           "VALUES (%s, %s, %s, %s, %s, %s)", oldTup)

		#print('1 done')
		connection.commit()
	#print('Done! (Hopefully)')
	return 0
