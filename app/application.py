from flask import (Flask, render_template, redirect, url_for, flash, request,
                   jsonify)
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_security import login_required
from sqlalchemy import create_engine, text
from settings import DB_URL, SECRET_KEY
from forms import RegistrationForm, LoginForm, PlaylistCreateForm
from flask_paginate import Pagination
import db_utils
import utils

app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
print("Connecting to {}".format(DB_URL))
engine = create_engine(DB_URL)

app.jinja_env.globals.update(format_duration=utils.format_duration)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check to make sure username not taken
        if db_utils.user_exists(engine, form.username.data):
            flash('Username already taken.', 'danger')
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
sqlforprofileplaylists = text('SELECT title, id '
                              'FROM playlists '
                              'WHERE user_id=(SELECT users.id FROM users '
                              '               WHERE users.username=:user)')


@app.route('/profile/<username>')
@login_required
def profile(username):
    if username is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    playlists = db_utils.user_playlists(engine, username)
    return render_template('profile.html',
                           user=current_user,
                           playlists=list(playlists))


@app.route('/playlist/<playlist_id>')
@login_required
def playlist(playlist_id):
    songs = db_utils.playlist_songs(engine, playlist_id)
    playlist = db_utils.playlist_details(engine, playlist_id)
    return render_template('playlist.html',
                           songs=list(songs),
                           playlist=playlist)


@app.route('/playlist/new', methods=['GET', 'POST'])
@login_required
def playlist_create():
    form = PlaylistCreateForm()
    if form.validate_on_submit():
        # Create playlist
        db_utils.create_playlist(engine,
                                 current_user.get_id(),
                                 form.title.data)
        return redirect(url_for('profile', username=current_user.username))
    return render_template('playlist_create.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    q = request.args.get('q')

    per_page = 25
    page = request.args.get('page', type=int, default=1)
    count, songs = db_utils.search_songs(engine, q, limit=per_page,
                                         offset=(page - 1) * per_page)
    pagination = Pagination(page=page,
                            total=count,
                            # search=search,
                            record_name='songs',
                            css_framework='bootstrap3',
                            per_page=per_page)
    playlists = db_utils.user_playlists(engine, current_user.username)
    return render_template('search_results.html',
                           songs=songs,
                           pagination=pagination,
                           query=(q if q else ''),
                           playlists=list(playlists)
                           )


@app.route('/playlist/add_song', methods=['POST'])
@login_required
def playlist_add():
    data = request.json
    song_id = data['song_id']
    playlist_id = data['playlist_id']
    db_utils.add_song_to_playlist(engine, song_id, playlist_id)
    return jsonify("Added successfully")


@app.route('/playlist/edit', methods=['PUT'])
@login_required
def playlist_edit():
    data = request.json
    playlist_id = data['playlist_id']
    new_title = data['title']
    db_utils.playlist_update(engine, playlist_id, new_title)
    return jsonify("Updated title")


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
