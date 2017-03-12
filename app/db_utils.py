from werkzeug.security import (generate_password_hash, check_password_hash)
from sqlalchemy import text
from user import User


def user_exists(engine, user):
    ''' Checks to see if a username already exists '''
    sql = text('SELECT COUNT(*) FROM `users` WHERE `username`=:user')
    with engine.connect() as con:
        res = con.execute(sql, user=user).fetchone()
        return res[0] != 0


def create_user(engine, user, password, email):
    ''' Creates a user with the given information; saves a hashed password '''
    sql = text('INSERT INTO `users` (`username`, `password_hash`, `email`)'
               'VALUES (:user, :pw_hash, :email)', autocommit=True)
    with engine.connect() as con:
        pw_hash = generate_password_hash(password)
        con.execute(sql, user=user, pw_hash=pw_hash, email=email)


def user_login(engine, user, password):
    '''
    Validates a password with a user. Checks that the hashed passwords match
    '''
    sql = text('SELECT `password_hash`, `id` FROM `users` WHERE `username`=:user')
    with engine.connect() as con:
        res = con.execute(sql, user=user).fetchone()
        if res and len(res) > 0 and check_password_hash(res[0], password):
            return get_user_by_id(engine, res[1])


def get_user_by_id(engine, user_id):
    sql = text('SELECT * FROM `users` WHERE `id`=:id')
    with engine.connect() as con:
        res = con.execute(sql, id=user_id).fetchone()
        if res:
            return User(user_id)
