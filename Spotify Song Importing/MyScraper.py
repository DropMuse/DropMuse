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
	print()
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

	Albums = spotify.artist_albums(ArtistID, album_type='single,album', limit='50')
	#Albums = set(Alb)
	print('# of Albums: ' + str(len(Albums['items'])))
	AlbumList = []																			#AlbumList contains all of the albums
	AlbumIDs = []
	for album in range(0, len(Albums['items'])):
		AlbumList.append(Albums['items'][album]['name'])
		AlbumIDs.append(Albums['items'][album]['id'])										#AlbumIDs contains all of the albumsIDs
		#print(Albums['items'][album]['id'])
		#print(AlbumList)
	#print()
	for eachAlbum in range(0, len(AlbumIDs)):
	#for eachAlbum in range(4, 5):
		#print(AlbumIDs[eachAlbum])
		albuminfo = spotify.album(AlbumIDs[eachAlbum])
		for track in range(0, len(albuminfo['tracks']['items'])):
			#print(AName)																								#Artist Name
			#print('Album Name: ' + AlbumList[eachAlbum])															#Album Name
			#print('SongID: ' + albuminfo['tracks']['items'][track]['id'])											#songID
			#print('Song Name: ' + albuminfo['tracks']['items'][track]['name'])										#Song Name
			#if(albuminfo['tracks']['items'][track]['preview_url'] != None):
			#	print('Preview URL: ' + albuminfo['tracks']['items'][track]['preview_url'])							#Preview URL
			#print('Duration: ' + str(albuminfo['tracks']['items'][track]['duration_ms']))					#Duration
			#print()

			tup = (albuminfo['tracks']['items'][track]['id'], AName.encode('utf-8'), AlbumList[eachAlbum].encode('utf-8'), 
                       albuminfo['tracks']['items'][track]['name'].encode('utf-8'), albuminfo['tracks']['items'][track]['preview_url'], 
                       albuminfo['tracks']['items'][track]['duration_ms']);
			cursor.execute("INSERT INTO songs_dev(spotify_id, artist, album, song, song_url, duration) "
                       "VALUES (%s, %s, %s, %s, %s, %s)", tup)

			#print('1 done')
			connection.commit()
	print('Done! (Hopefully)')
	return 0

