from sqlalchemy import text
from lyrics import get_lyrics, get_sentiment
from audio import get_audio_analysis
import string
import json


def update_songs_table(engine):
    # Query songs that don't have sentiment or lyrics or audio analysis
    sql = text('SELECT id, artist, title, preview_url '
               'FROM songs '
               'WHERE ((lyrics IS NULL) AND (pos IS NULL) '
               '      AND (tempo IS NULL)) '
               '      OR (preview_url IS NOT NULL AND wave_info IS NULL);')

    con = engine.connect()
    result = list(con.execute(sql).fetchall())

    print "Running analysis on {} songs".format(len(result))

    printable = set(string.printable)

    for res in result:
        song_id = res['id']
        artist = res['artist']
        song = res['title']
        preview_url = res['preview_url']

        print "* Doing analysis for '{}/{}'".format(
            artist.encode('utf-8'), song.encode('utf-8'))

        lyrics = get_lyrics(artist, song)
        if(lyrics is None):
            print("Could not find lyrics for " + song)
        else:
            lyrics = ''.join(filter(lambda x: x in printable, lyrics))
        sentiment = get_sentiment(lyrics)
        print "Got sentiment for " + song
        tempo, pitch, harm, perc, wave = get_audio_analysis(preview_url)
        print "Got audio data for " + song

        sql = text('UPDATE songs '
                   'SET lyrics=:lyrics, pos=:pos, neg=:neg, neu=:neu, '
                   '    compound=:compound, tempo=:tempo, '
                   '    pitch=:pitch, harmonic=:harmonic, '
                   '    percussive=:percussive, wave_info=:wave '
                   'WHERE id=:song_id;', autocommit=True)
        con.execute(sql,
                    lyrics=str(lyrics) if lyrics else None,
                    pos=sentiment['pos'],
                    neg=sentiment['neg'],
                    neu=sentiment['neu'],
                    compound=sentiment['compound'],
                    tempo=tempo,
                    pitch=pitch,
                    harmonic=harm,
                    percussive=perc,
                    song_id=song_id,
                    wave=json.dumps(wave))
    print 'Finished updating songs table!'
