from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_security import login_required
from sqlalchemy import create_engine, text
from settings import (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DBNAME,
                      DB_PREFIX, SECRET_KEY)
from forms import RegistrationForm, LoginForm
import db_utils

app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
conn_str = "{}{}:{}@{}:{}/{}".format(DB_PREFIX,
                                     DB_USER,
                                     DB_PASS,
                                     DB_HOST,
                                     DB_PORT,
                                     DB_DBNAME)
print("Connecting to {}".format(conn_str))
engine = create_engine(conn_str)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check to make sure username not taken
        if db_utils.user_exists(engine, form.username.data):
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        # Create user
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
    form = LoginForm()
    if form.validate_on_submit():
        # Validate user login
        user = db_utils.user_login(engine,
                                   form.username.data,
                                   form.password.data)
        if user:
            # Login user with Flask-Login
            login_user(user)
            flash('You have been logged in.', 'success')
            return redirect(url_for('profile', username=form.username.data))
        else:
            flash('Invalid password', 'warning')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ADVANCED QUERY
sqlforprofileplaylists = text('SELECT title,external_url '
                              'FROM playlists '
                              'WHERE user_id=(SELECT user_id FROM users '
                              '               WHERE username=:user)')

@app.route('/profile/<username>')
@login_required
def profile(username):
    with engine.connect() as con:
        if username is None:
            flash('User %s not found.' % username)
            return redirect(url_for('index'))
        playlists = con.execute(sqlforprofileplaylists, user=username)
        return render_template('profile.html',
                               user=current_user,
                               playlists=playlists)



sqlforplaylistsongs = text('SELECT * FROM songs'
                           'JOIN playlist_entry ON songs.playlist_id = playlist_entry.playlist_id'
                           'WHERE playlist_entry.playlist_id = id') #ADVANCED
@app.route('/playlist/<id>')
@login_required
def playlist(id):
    with engine.connect() as con:
        songs = con.execute(sqlforplaylistsongs)
        return render_template('playlist.html', songs = songs, id=id)


@login_manager.user_loader
def load_user(user_id):
    user = db_utils.get_user_by_id(engine, user_id)
    return user


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')
