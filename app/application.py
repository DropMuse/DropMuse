from flask import (Flask, render_template, redirect, url_for, flash, request,
                   jsonify)
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_security import login_required
from sqlalchemy import create_engine
from settings import DB_URL, SECRET_KEY, SERVER_NAME, SERVER_ENV
from forms import RegistrationForm, LoginForm, PlaylistCreateForm
from flask_paginate import Pagination
import db_utils
import utils
import recommendation
from .spotify import (spotify_blueprint, get_spotify_playlists,
                      create_spotify_playlist)
from scheduler import DropmuseScheduler
import logging
logging.basicConfig()

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['TEMPLATES_AUTO_RELOAD'] = True
if SERVER_ENV != 'dev':
    app.config['SERVER_NAME'] = SERVER_NAME
app.register_blueprint(spotify_blueprint, url_prefix='/spotify')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You must be logged in to see this page.'
login_manager.login_message_category = 'warning'

print("Connecting to {}".format(DB_URL))
engine = create_engine(DB_URL, encoding='utf-8')

scheduler = DropmuseScheduler(engine)

app.jinja_env.globals.update(format_duration=utils.format_duration)
app.jinja_env.filters.update(escapejs=utils.jinja2_escapejs_filter)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    else:
        return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
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
    entries = db_utils.playlist_songs(engine, playlist_id)
    playlist = db_utils.playlist_details(engine, playlist_id)
    return render_template('playlist.html',
                           entries=list(entries),
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


@app.route('/playlist/recommendations/<playlist_id>', methods=['GET', 'POST'])
@login_required
def playlist_recommendations(playlist_id):
    playlist_id = int(playlist_id)
    song_ids = recommendation.get_recommendations(engine, playlist_id)
    playlist_existing = db_utils.playlist_songs(engine, playlist_id)
    for p in playlist_existing:
        if p.song_id in song_ids:
            song_ids.remove(p.song_id)
    song_ids = song_ids[:25]
    songs = db_utils.song_details_many(engine, song_ids)
    return render_template('playlist_recommendations.html',
                           recommendations=list(songs),
                           playlist_id=playlist_id)


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
def playlist_song_add():
    data = request.json
    song_id = data['song_id']
    playlist_id = data['playlist_id']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to edit this playlist', 'danger')
        return '', 403

    db_utils.add_song_to_playlist(engine, song_id, playlist_id)
    return jsonify("Added successfully")


@app.route('/playlist/export_playlist', methods=['POST'])
@login_required
def playlist_export():
    data = request.json
    playlist_id = data['playlist_id']

    current_playlist_name = db_utils.get_playlist_name(engine, playlist_id)
    playlist_existing = db_utils.playlist_songs(engine, playlist_id)
    tracks_to_add = []
    for p in playlist_existing:
        if(p.spotify_id is not None):
            tracks_to_add.append(p.spotify_id)

    create_spotify_playlist(current_playlist_name[0], tracks_to_add)
    return jsonify("Exported successfully")


@app.route('/playlist/import_playlists', methods=['GET'])
@login_required
def import_playlists():
    playlists = get_spotify_playlists()
    return render_template('import_playlist_selection.html',
                           playlists=playlists['items'])


@app.route('/playlist/import_playlists/<playlist_id>', methods=['GET'])
@login_required
def import_single_playlist(playlist_id):
    playlists = get_spotify_playlists()
    user_spotify = current_user.spotify

    try:
        playlist = next(p for p in playlists['items']
                        if p['id'] == playlist_id)
    except:
        flash("Couldn't find playlist", "warning")
        return redirect(url_for('profile', username=current_user.username))

    if playlist['owner']['id'] == user_spotify.current_user()['id']:
        # insert playlist into database
        db_utils.create_playlist(engine, current_user.id, playlist['name'])
        user_id = user_spotify.current_user()['id']
        results = current_user.spotify.user_playlist(user_id,
                                                     playlist['id'],
                                                     fields="tracks")
        tracks = results['tracks']
        curr_playlist_id = db_utils.get_playlist_id(engine,
                                                    playlist['name'],
                                                    current_user.id)

        for item in tracks['items']:
            # Skip local songs
            if item['is_local']:
                continue
            track = item['track']
            trackname = track['name']
            trackalbum = track['album']['name']
            trackexternalurl = track['external_urls'].get('spotify')
            trackartist = track['artists'][0]['name']
            trackduration = track.get('duration_ms', 0) / 1000
            trackpreview = track.get('preview_url')
            trackuri = track['uri']

            # insert song into database
            db_utils.create_song(engine, trackname, trackartist,
                                 trackalbum, trackexternalurl,
                                 trackduration, trackpreview, trackuri)
            curr_song_id = db_utils.get_song_id(engine, trackname,
                                                trackartist)

            # insert song into playlist.
            db_utils.add_song_to_playlist(engine, curr_song_id[0],
                                          curr_playlist_id[0])
    flash("Imported playlist: {}".format(playlist['name']), 'success')

    # Update the database once we've imported new songs
    scheduler.schedule_update()

    return redirect(url_for('profile', username=current_user.username))


@app.route('/playlist/remove_song', methods=['POST'])
@login_required
def playlist_song_remove():
    data = request.json
    entry_position = data['entry_position']
    playlist_id = data['playlist_id']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to edit this playlist', 'danger')
        return '', 403

    db_utils.remove_song_from_playlist(engine, entry_position, playlist_id)
    return jsonify("Removed successfully")


@app.route('/playlist/move_song', methods=['POST'])
@login_required
def playlist_song_move():
    data = request.json
    old_position = data['old_position']
    new_position = data['new_position']
    playlist_id = data['playlist_id']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to edit this playlist', 'danger')
        return '', 403

    db_utils.move_song_in_playlist(engine,
                                   old_position,
                                   new_position,
                                   playlist_id)
    return jsonify("Moved successfully")


@app.route('/playlist/set_vote', methods=['POST'])
@login_required
def playlist_set_vote():
    data = request.json
    position = data['position']
    vote_status = data['status']
    playlist_id = data['playlist_id']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to edit this playlist', 'danger')
        return '', 403

    if vote_status:
        db_utils.create_vote(engine, playlist_id, position)
    else:
        db_utils.delete_vote(engine, playlist_id, position)
    return jsonify("Vote changed successfully")


@app.route('/profile/remove_playlist', methods=['POST'])
@login_required
def playlist_remove():
    data = request.json
    user_id = data['user_id']
    playlist_id = data['playlist_id']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to delete this playlist', 'danger')
        return '', 403

    db_utils.remove_playlist_from_user(engine, user_id, playlist_id)
    return jsonify("Removed successfully")


@app.route('/playlist/edit', methods=['PUT'])
@login_required
def playlist_edit():
    data = request.json
    playlist_id = data['playlist_id']
    new_title = data['title']

    # Authenticate user
    details = db_utils.playlist_details(engine, playlist_id)
    if (not details) or details.user_id != current_user.id:
        flash('Not authorized to edit this playlist', 'danger')
        return '', 403

    db_utils.playlist_update(engine, playlist_id, new_title)
    return jsonify("Updated title")


@app.route('/songs/<song_id>')
@login_required
def song_info(song_id):
    song = db_utils.song_by_id(engine, song_id)
    keywords = db_utils.song_keywords(engine, song_id)
    return render_template('song.html',
                           song=song,
                           keywords=list(keywords))


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
