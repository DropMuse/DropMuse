from flask import Blueprint, redirect, url_for, request
from settings import (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SERVER_NAME)
# import spotipy
from flask_login import current_user
from flask_security import login_required
from spotipy import oauth2
import db_utils
import application as app

spotify_blueprint = Blueprint('spotify', __name__, template_folder='templates')
SCOPE = ""

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
