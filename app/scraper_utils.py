from sqlalchemy import text
from lyrics import get_lyrics, get_sentiment
from audio import get_audio_analysis
import string


def update_songs_table(engine):
    # Query songs that don't have sentiment or lyrics or audio analysis
    sql = text('SELECT id, artist, title, preview_url '
               'FROM songs '
               'WHERE lyrics IS NULL OR pos IS NULL OR tempo IS NULL AND id > 3457;')

    con = engine.connect()
    result = con.execute(sql).fetchall()

    for res in result:
        song_id = res['id']
        artist = res['artist']
        song = res['title']
        preview_url = res['preview_url']

        print "Doing analysis for '{}/{}'".format(
            artist.encode('utf-8'), song.encode('utf-8'))

        printable = set(string.printable)
        lyrics = get_lyrics(artist, song)
        if(lyrics is None):
            print("Could not find lyrics for " + song)
        else:
            lyrics = ''.join(filter(lambda x: x in printable, lyrics))
        sentiment = get_sentiment(lyrics)
        tempo, pitch, harmonic, percussive = get_audio_analysis(preview_url)

        sql = text('UPDATE songs '
                   'SET lyrics=:lyrics, pos=:pos, neg=:neg, neu=:neu, '
                   '    compound=:compound, tempo=:tempo, '
                   '    pitch=:pitch, harmonic=:harmonic, '
                   '    percussive=:percussive '
                   'WHERE id=:song_id;', autocommit=True)
        con.execute(sql,
                    lyrics=str(lyrics),
                    pos=sentiment['pos'],
                    neg=sentiment['neg'],
                    neu=sentiment['neu'],
                    compound=sentiment['compound'],
                    tempo=tempo,
                    pitch=pitch,
                    harmonic=harmonic,
                    percussive=percussive,
                    song_id=song_id)
