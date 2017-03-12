from flask import Flask, render_template, request, redirect, url_for, flash
import sqlalchemy
from sqlalchemy import create_engine, text
from settings import (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DBNAME,
                      DB_PREFIX, SECRET_KEY)
from forms import RegistrationForm, LoginForm
import db_utils

app = Flask(__name__)
app.secret_key = SECRET_KEY
conn_str = "{}{}:{}@{}:{}/{}".format(DB_PREFIX,
                                     DB_USER,
                                     DB_PASS,
                                     DB_HOST,
                                     DB_PORT,
                                     DB_DBNAME)
engine = create_engine(conn_str)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if db_utils.user_exists(engine, form.username.data):
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        else:
            db_utils.create_user(engine,
                                 form.username.data,
                                 form.password.data,
                                 form.email.data)
            flash('Thanks for registering', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO: Validate user login
        flash('You have been logged in.')
        return redirect(url_for('profile'))
    return render_template('login.html', form=form)



sqlforprofileuser = text('SELECT username FROM users WHERE username = username')
sqlforprofileplaylists = text('SELECT title,external_url FROM playlists WHERE user_id = theuser (SELECT user_id as theuser FROM users WHERE username = username)') #ADVANCED

@app.route('/profile/<username>')
@login_required
def profile(username):
    profile = db.engine.execute(sqlforprofileuser)
    if username == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    playlists = db.engine.execute(sqlforprofileplaylists)
    return render_template('profile.html', username=username, playlists=playlists)

@app.route('/playlist')
def profile():
    return render_template('playlist.html')
