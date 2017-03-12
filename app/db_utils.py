from werkzeug.security import (generate_password_hash, check_password_hash)


def user_exists(conn, user):
    ''' Checks to see if a username already exists '''
    sql = 'SELECT COUNT(*) FROM `users` WHERE `username`=%s'
    with conn.cursor() as cursor:
        cursor.execute(sql, (user,))
        count = cursor.fetchone().get('COUNT(*)')
        print count
        return count != 0


def create_user(conn, user, password, email):
    ''' Creates a user with the given information; saves a hashed password '''
    sql = 'INSERT INTO `users` (`username`, `password_hash`, `email`)' \
          'VALUES (%s, %s, %s)'
    with conn.cursor() as cursor:
        pw_hash = generate_password_hash(password)
        cursor.execute(sql, (user, pw_hash, email))
    conn.commit()


def validate_password(conn, user, password):
    '''
    Validates a password with a user. Checks that the hashed passwords match
    '''
    sql = 'SELECT `password` FROM `users` WHERE `username`=%s'
    with conn.cursor() as cursor:
        cursor.execute(sql, (user,))
        user = cursor.fetchone()
        if user:
            return check_password_hash(user['password'], password)
