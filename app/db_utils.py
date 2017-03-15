from werkzeug.security import (generate_password_hash, check_password_hash)
from sqlalchemy import text
from models import User, Playlist


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


def create_playlist(engine, user_id, playlist_title):
    '''
    Creates a playlist in the given user's account
    '''
    sql = text('INSERT INTO playlists (title, user_id) '
               'VALUES (:title, :user_id)', autocommit=True)
    with engine.connect() as con:
        con.execute(sql, user_id=user_id, title=playlist_title)

def search_songs(engine, query, limit=100, offset=0):
    '''
    Performs search query on songs
    '''
    query = "%{}%".format(query.lower())
    sql = text("SELECT * "
               "FROM songs "
               "WHERE LOWER(title) LIKE :query "
               "      OR LOWER(artist) LIKE :query "
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
    sql = text('INSERT INTO playlist_entry (song_id, playlist_id) '
               'VALUES (:song_id, :playlist_id)', autocommit=True)

    with engine.connect() as con:
        con.execute(sql, song_id=song_id, playlist_id=playlist_id)


def remove_song_from_playlist(engine, song_id, playlist_id):
    ''' Removes song to the given playlist '''
    sql = text('DELETE FROM playlist_entry '
               'WHERE playlist_entry.song_id=:song_id '
               'AND playlist_entry.playlist_id=:playlist_id', autocommit=True)

    with engine.connect() as con:
        con.execute(sql, song_id=song_id, playlist_id=playlist_id)

def remove_playlist_from_user(engine, user_id, playlist_id):
    ''' Removes playlist based on user_id '''
    sql = text('DELETE FROM playlists '
               'WHERE playlists.user_id=:user_id '
               'AND playlists.id=:playlist_id', autocommit=True)

    with engine.connect() as con:
        con.execute(sql, user_id=user_id, playlist_id=playlist_id)



def playlist_songs(engine, playlist_id):
    # ADVANCED
    sqlforplaylistsongs = text('SELECT * FROM songs '
                               'JOIN playlist_entry '
                               'ON songs.id=playlist_entry.song_id '
                               'WHERE playlist_entry.playlist_id=:playlist_id')
    with engine.connect() as con:
        return con.execute(sqlforplaylistsongs, playlist_id=playlist_id)


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
