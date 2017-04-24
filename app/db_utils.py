from werkzeug.security import (generate_password_hash, check_password_hash)
from sqlalchemy import text
from models import User, Playlist
import json


def user_exists(engine, user):
    ''' Checks to see if a username already exists '''
    sql = text('SELECT COUNT(*) FROM users WHERE username=:user')
    with engine.connect() as con:
        res = con.execute(sql, user=user).fetchone()
        return res[0] != 0


def create_user(engine, user, password, email):
    ''' Creates a user with the given information; saves a hashed password '''
    sql = text('INSERT INTO users (username, password_hash, email)'
               'VALUES (:user, :pw_hash, :email)', autocommit=True)
    with engine.connect() as con:
        pw_hash = generate_password_hash(password)
        con.execute(sql, user=user, pw_hash=pw_hash, email=email)


def user_login(engine, user, password):
    '''
    Validates a password with a user. Checks that the hashed passwords match
    '''
    sql = text('SELECT password_hash, id '
               'FROM users '
               'WHERE username=:user')
    with engine.connect() as con:
        res = con.execute(sql, user=user).fetchone()
        if res and len(res) > 0 and check_password_hash(res[0], password):
            return get_user_by_id(engine, res[1])


def get_user_by_id(engine, user_id):
    '''
    Creates a User object for user with id of user_id
    '''
    sql = text('SELECT id, username FROM users WHERE id=:id')
    with engine.connect() as con:
        res = con.execute(sql, id=user_id).fetchone()
        if res:
            return User(user_id, username=res[1])


def create_playlist(engine, user_id, title):
    '''
    Creates a playlist in the given user's account
    '''
    sql = text('INSERT INTO playlists (title, user_id) '
               'SELECT :title, :user_id FROM DUAL WHERE '
               'NOT EXISTS (SELECT 1 FROM playlists WHERE title=:title '
               '            AND user_id=:user_id)', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, user_id=user_id, title=title)


def search_songs(engine, query, limit=100, offset=0):
    '''
    Performs search query on songs
    '''
    query = "%{}%".format(query.lower())
    sql = text("SELECT * "
               "FROM songs "
               "WHERE LOWER(title) LIKE :query "
               "      OR LOWER(artist) LIKE :query "
               "      OR id IN (SELECT song_id "
               "                FROM keywords "
               "                WHERE word LIKE :query)"
               "LIMIT :limit OFFSET :offset")
    sql_count = text("SELECT COUNT(*) "
                     "FROM songs "
                     "WHERE LOWER(title) LIKE :query "
                     "      OR LOWER(artist) LIKE :query ")
    with engine.connect() as con:
        results = con.execute(sql,
                              query=query,
                              offset=offset,
                              limit=limit)
        results_count = con.execute(sql_count, query=query).fetchone()[0]
        return results_count, list(results)


def create_follower(engine, follower, user_followed):
    sql = text('INSERT INTO following(user_id, following_id) '
               'VALUES (:follower, :user_followed) '
               'ON DUPLICATE KEY UPDATE user_id=user_id',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql,
                    follower=follower,
                    user_followed=user_followed)

def get_user_followers(engine, user_id):
    sql = text('SELECT * '
               'FROM users '
               'LEFT JOIN following '
               'ON users.id=following.following_id '
               'WHERE following.user_id=:user_id')
    with engine.connect() as con:
        return con.execute(sql, user_id=user_id)

def get_user_followings(engine, user_id):
    sql = text('SELECT * '
               'FROM users '
               'LEFT JOIN following '
               'ON users.id=following.user_id '
               'WHERE following.following_id=:user_id')
    with engine.connect() as con:
        return con.execute(sql, user_id=user_id)


def search_users(engine, query):
    query = '%{}%'.format(query.lower())
    sql = text('SELECT * '
               'FROM users '
               'WHERE LOWER(username) LIKE :query;')
    with engine.connect() as con:
        return list(con.execute(sql, query=query).fetchall())


def user_playlists(engine, username):
    ''' Returns the playlists of a user '''
    # ADVANCED
    profile_plists = text('SELECT playlists.*, COUNT(songs.id), SUM(duration) '
                          'FROM playlists '
                          'LEFT JOIN playlist_entry '
                          'ON playlists.id=playlist_entry.playlist_id '
                          'LEFT JOIN songs '
                          'ON playlist_entry.song_id=songs.id '
                          'WHERE playlists.user_id=(SELECT users.id '
                          '                         FROM users '
                          '                         WHERE username=:user) '
                          'GROUP BY playlists.id')
    with engine.connect() as con:
        playlists = []
        for p in con.execute(profile_plists, user=username):
            playlists.append(Playlist(p.id,
                                      title=p.title,
                                      count=p['COUNT(songs.id)'],
                                      duration=p['SUM(duration)']))
        return playlists

def add_song_to_playlist(engine, song_id, playlist_id):
    ''' Adds song to the given playlist '''
    sql = text('INSERT INTO playlist_entry (song_id, playlist_id, position) '
               'SELECT :song_id, :playlist_id, (IFNULL(MAX(position), 0) + 1) '
               'FROM playlist_entry '
               'WHERE playlist_id=:playlist_id', autocommit=True)

    with engine.connect() as con:
        con.execute(sql, song_id=song_id, playlist_id=playlist_id)


def create_song(engine, title, artist, album, duration, preview_url,
                spotify_id):
    ''' Creates a song with the given information'''
    sql = text('INSERT INTO songs (title, artist, album, duration, '
               '                   preview_url, spotify_id) '
               'SELECT :title, :artist, :album, :duration, :preview_url, '
               '       :spotify_id '
               'FROM DUAL '
               'WHERE NOT EXISTS (SELECT 1 FROM songs WHERE title=:title '
               '                  AND artist=:artist '
               '                  AND album=:album '
               '                  AND spotify_id=:spotify_id)',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql, title=title, artist=artist, album=album,
                    duration=duration, preview_url=preview_url,
                    spotify_id=spotify_id)


def remove_song_from_playlist(engine, position, playlist_id):
    ''' Removes song to the given playlist '''
    sql = text('DELETE FROM playlist_entry '
               'WHERE playlist_entry.position=:position '
               'AND playlist_entry.playlist_id=:playlist_id', autocommit=True)
    sql2 = text('UPDATE playlist_entry '
                'SET position = position - 1 '
                'WHERE position>:position '
                'AND playlist_id=:playlist_id', autocommit=True)

    with engine.connect() as con:
        con.execute(sql, position=position, playlist_id=playlist_id)
        con.execute(sql2, position=position, playlist_id=playlist_id)


def move_song_in_playlist(engine, old_position, new_position, playlist_id):
    # No action needed
    if new_position == old_position:
        return
    # Need to shift entries back
    elif new_position > old_position:
        sql = text('UPDATE playlist_entry '
                   'SET position=position-1 '
                   'WHERE position>:old_pos AND position<=:new_pos '
                   'AND playlist_id=:playlist_id '
                   'ORDER BY position', autocommit=True)
    # Need to shift entries forward
    else:
        sql = text('UPDATE playlist_entry '
                   'SET position=position+1 '
                   'WHERE position<:old_pos AND position>=:new_pos '
                   'AND playlist_id=:playlist_id '
                   'ORDER BY position DESC', autocommit=True)
    remove = text('UPDATE playlist_entry '
                  'SET position=-1 '
                  'WHERE position=:old_pos '
                  'AND playlist_id=:playlist_id', autocommit=True)
    replace = text('UPDATE playlist_entry '
                   'SET position=:new_pos '
                   'WHERE position=-1 '
                   'AND playlist_id=:playlist_id', autocommit=True)
    with engine.connect() as con:
        # Swap moving entry to -1
        con.execute(remove, old_pos=old_position, playlist_id=playlist_id)
        # Move all in-between entries
        con.execute(sql,
                    old_pos=old_position,
                    new_pos=new_position,
                    playlist_id=playlist_id)
        # Swap moving entry to correct position
        con.execute(replace, new_pos=new_position, playlist_id=playlist_id)


def remove_playlist_from_user(engine, user_id, playlist_id):
    ''' Removes playlist based on user_id '''
    sql = text('DELETE FROM playlists '
               'WHERE playlists.user_id=:user_id '
               'AND playlists.id=:playlist_id', autocommit=True)
    sql2 = text('DELETE FROM playlist_entry '
                'WHERE playlist_entry.playlist_id=:playlist_id',
                autocommit=True)
    with engine.connect() as con:
        con.execute(sql2, playlist_id=playlist_id)
        con.execute(sql, user_id=user_id, playlist_id=playlist_id)


def playlist_songs(engine, playlist_id):
    # ADVANCED
    sql = text('SELECT *, votes.position AS vposition FROM songs '
               'JOIN playlist_entry '
               'ON songs.id=playlist_entry.song_id '
               'LEFT JOIN votes '
               'ON playlist_entry.position=votes.position '
               'AND playlist_entry.playlist_id=votes.playlist_id '
               'WHERE playlist_entry.playlist_id=:playlist_id '
               'ORDER BY playlist_entry.position')
    with engine.connect() as con:
        return con.execute(sql, playlist_id=playlist_id)


def get_playlist_id(engine, playlist_name, uid):
    sql = text('SELECT id '
               'FROM playlists '
               'WHERE title=:playlist_name AND user_id=:uid')
    with engine.connect() as con:
        query = con.execute(sql, playlist_name=playlist_name, uid=uid)
        return query.fetchone()


def user_from_username(engine, username):
    ''' Checks to see if a username already exists '''
    sql = text('SELECT * FROM users WHERE username=:username')
    with engine.connect() as con:
        res = con.execute(sql, username=username)
    return res.fetchone()


def get_playlist_name(engine, playlist_id):
    sql = text('SELECT title '
               'FROM playlists '
               'WHERE id=:playlist_id')
    with engine.connect() as con:
        query = con.execute(sql, playlist_id=playlist_id)
        return query.fetchone()


def get_song_id(engine, trackname, trackartist):
    sql = text('SELECT id '
               'FROM songs '
               'WHERE title=:trackname AND artist=:trackartist')
    with engine.connect() as con:
        query = con.execute(sql, trackname=trackname, trackartist=trackartist)
        return query.fetchone()


def playlist_details(engine, playlist_id):
    sql = text('SELECT * '
               'FROM playlists '
               'WHERE id=:playlist_id')
    with engine.connect() as con:
        return con.execute(sql, playlist_id=playlist_id).fetchone()


def playlist_update(engine, playlist_id, title):
    sql = text('UPDATE playlists '
               'SET title=:title '
               'WHERE id=:playlist_id', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, playlist_id=playlist_id, title=title)


def song_by_id(engine, song_id):
    sql = text('SELECT * '
               'FROM songs '
               'WHERE id=:song_id')
    with engine.connect() as con:
        return con.execute(sql, song_id=song_id).fetchone()


def spotify_credentials_upsert(engine, user_id, token_info):
    sql = text('INSERT INTO spotify_credentials(user_id, token_info) '
               'VALUES (:user_id, :token_info) '
               'ON DUPLICATE KEY UPDATE token_info=:token_info;',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql, user_id=user_id, token_info=json.dumps(token_info))


def spotify_creds_for_user(engine, user_id):
    sql = text('SELECT token_info '
               'FROM spotify_credentials '
               'WHERE user_id=:user_id;')
    with engine.connect() as con:
        res = con.execute(sql, user_id=user_id).first()
        if res:
            return json.loads(res[0])


def spotify_creds_delete(engine, user_id):
    sql = text('DELETE FROM spotify_credentials '
               'WHERE user_id=:user_id;',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql, user_id=user_id)


def song_max_id(engine):
    sql = text('SELECT MAX(id) '
               'FROM songs;')
    with engine.connect() as con:
        return con.execute(sql).fetchone()[0]


def playlist_max_id(engine):
    sql = text('SELECT MAX(id) '
               'FROM playlists;')
    with engine.connect() as con:
        return con.execute(sql).fetchone()[0]


def get_playlist_interactions(engine):
    '''
    Returns playlist entries joined with their votes
    '''
    sql = text('SELECT playlist_entry.playlist_id AS playlist_id, '
               '       votes.position AS vote, '
               '       playlist_entry.song_id as song_id '
               'FROM playlist_entry '
               'LEFT JOIN votes '
               'ON votes.playlist_id=playlist_entry.playlist_id '
               'AND votes.position=playlist_entry.position;')
    with engine.connect() as con:
        return con.execute(sql)


def create_vote(engine, playlist_id, position):
    sql = text('INSERT IGNORE INTO votes(playlist_id, position) '
               'VALUES (:playlist_id, :position)', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, playlist_id=playlist_id, position=position)


def delete_vote(engine, playlist_id, position):
    sql = text('DELETE FROM  votes '
               'WHERE playlist_id=:playlist_id '
               'AND position=:position', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, playlist_id=playlist_id, position=position)


def song_sentiments(engine):
    sql = text('SELECT id, pos, neg, neu '
               'FROM songs;')
    with engine.connect() as con:
        return con.execute(sql).fetchall()


def song_artists(engine):
    sql = text('SELECT id, artist '
               'FROM songs;')
    with engine.connect() as con:
        return con.execute(sql).fetchall()


def song_details_many(engine, song_ids):
    sql = text('SELECT * '
               'FROM songs '
               'WHERE id IN :song_ids')
    with engine.connect() as con:
        results = list(con.execute(sql, song_ids=song_ids).fetchall())
        ordered = []
        for i in song_ids:
            try:
                ordered.append(next(res for res in results if res.id == i))
            except StopIteration:
                print("Couldn't find song {}'s details".format(i))
        return ordered


def song_lyrics(engine):
    sql = text('SELECT id, lyrics '
               'FROM songs;')
    with engine.connect() as con:
        return con.execute(sql).fetchall()


def delete_song_keywords(engine, song_id):
    sql = text('DELETE FROM keywords WHERE song_id=:song_id;', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, song_id=song_id)


def all_keywords(engine):
    sql = text('SELECT * '
               'FROM keywords;')
    with engine.connect() as con:
        return con.execute(sql).fetchall()


def song_keywords(engine, song_id):
    sql = text('SELECT * '
               'FROM keywords '
               'WHERE song_id=:song_id;')
    with engine.connect() as con:
        return con.execute(sql, song_id=song_id).fetchall()


def add_song_keyword(engine, song_id, keyword, weight):
    '''
    keyword_tupes:
        in form (keyword, weight)
    '''
    sql = text('INSERT INTO keywords(song_id, word, weight)'
               'VALUES (:song_id, :keyword, :weight) '
               'ON DUPLICATE KEY UPDATE weight=:weight;',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql, song_id=song_id, keyword=keyword, weight=weight)


def get_wave_info(engine, song_id):
    sql = text('SELECT wave_info '
               'FROM songs '
               'WHERE id=:song_id;')

    with engine.connect() as con:
        return con.execute(sql, song_id=song_id).fetchall()


def song_audio_features(engine):
    sql = text('SELECT id, (tempo - min_tempo) / (max_tempo - min_tempo) t, '
               '       (pitch - min_pitch) / (max_pitch - min_pitch) pi, '
               '       (harmonic - min_harm) / (max_harm - min_harm) h, '
               '       (percussive - min_perc) / (max_perc - min_perc) pe '
               'FROM songs, ('
               '    SELECT MIN(tempo) min_tempo, MAX(tempo) max_tempo, '
               '           MIN(pitch) min_pitch, MAX(pitch) max_pitch, '
               '           MIN(harmonic) min_harm, MAX(harmonic) max_harm, '
               '           MIN(percussive) min_perc, MAX(percussive) max_perc '
               '    FROM songs '
               '    WHERE tempo IS NOT NULL AND pitch IS NOT NULL AND '
               '          percussive IS NOT NULL AND harmonic IS NOT NULL '
               '    ) min_max')
    with engine.connect() as con:
        return con.execute(sql).fetchall()


def create_follower(engine, follower, user_followed):
    sql = text('INSERT INTO following(user_id, following_id) '
               'VALUES (:follower, :user_followed) '
               'ON DUPLICATE KEY UPDATE user_id=user_id',
               autocommit=True)
    with engine.connect() as con:
        con.execute(sql,
                    follower=follower,
                    user_followed=user_followed)
