from flask import Blueprint, redirect, url_for, request
from settings import (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SERVER_NAME)
from flask_login import current_user
from flask_security import login_required
from spotipy import oauth2
import db_utils
import application as app

spotify_blueprint = Blueprint('spotify', __name__, template_folder='templates')
SCOPE = ' '.join(["playlist-read-private",
                  "playlist-modify-public",
                  "playlist-modify-private",
                  "user-library-read"])

redirect_uri = 'http://' + SERVER_NAME + '/spotify/callback'
sp_oauth = oauth2.SpotifyOAuth(SPOTIFY_CLIENT_ID,
                               SPOTIFY_CLIENT_SECRET,
                               redirect_uri,
                               scope=SCOPE)


@spotify_blueprint.route('/authenticate')
@login_required
def start_authentication():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@spotify_blueprint.route('/callback')
@login_required
def auth_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    db_utils.spotify_credentials_upsert(app.engine,
                                        current_user.id,
                                        token_info)
    return redirect(url_for('profile', username=current_user.username))


@spotify_blueprint.route('/disconnect')
@login_required
def disconnect():
    db_utils.spotify_creds_delete(app.engine, current_user.id)
    current_user._spotify = None
    return redirect(url_for('profile', username=current_user.username))


def get_spotify_playlists():
    user_spotify = current_user.spotify
    playlists = user_spotify.current_user_playlists()
    return playlists


def create_spotify_playlist(current_playlist_name, tracks_to_add):
    user_spotify = current_user.spotify
    created = user_spotify.user_playlist_create(user_spotify.me()['id'],
                                                current_playlist_name)
    user_spotify.user_playlist_add_tracks(user_spotify.me()['id'],
                                          created['id'],
                                          tracks_to_add)


def do_playlist_import(engine, user_spotify, user_id, playlist_id,
                       scheduler):
    playlists = user_spotify.current_user_playlists()
    playlist = next(p for p in playlists['items']
                    if p['id'] == playlist_id)

    if playlist['owner']['id'] == user_spotify.current_user()['id']:
        # insert playlist into database
        db_utils.create_playlist(engine, user_id, playlist['name'])
        spotify_user_id = user_spotify.current_user()['id']
        results = user_spotify.user_playlist_tracks(spotify_user_id,
                                                    playlist['id'])
        tracks = results['items']

        while results['next']:
            results = user_spotify.next(results)
            tracks.extend(results['items'])

        curr_playlist_id = db_utils.get_playlist_id(engine,
                                                    playlist['name'],
                                                    user_id)

        for item in tracks:
            # Skip local songs
            if item['is_local']:
                continue
            track = item['track']
            trackname = track['name']
            trackalbum = track['album']['name']
            trackartist = track['artists'][0]['name']
            trackduration = track.get('duration_ms', 0) / 1000
            trackpreview = track.get('preview_url')
            trackuri = track['uri']

            # insert song into database
            db_utils.create_song(engine, trackname, trackartist,
                                 trackalbum, trackduration, trackpreview,
                                 trackuri)
            curr_song_id = db_utils.get_song_id(engine, trackname,
                                                trackartist)

            # insert song into playlist.
            db_utils.add_song_to_playlist(engine, curr_song_id[0],
                                          curr_playlist_id[0])

    # Update the database once we've imported new songs
    scheduler.schedule_update()
