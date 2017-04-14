from flask_login import UserMixin
import spotify
import spotipy
import db_utils
import application as app


class User(UserMixin):
    ''' User class for Flask-Login '''
    def __init__(self, user_id, username=None):
        self.id = int(user_id)
        self.username = username
        self._spotify = None

    @property
    def spotify(self):
        oa_client = spotify.sp_oauth
        # Fetch credentials from database
        if not self._spotify:
            self._spotify = db_utils.spotify_creds_for_user(app.engine,
                                                            self.id)
        # No credentials exist for user
        if self._spotify is None:
            return None
        # Refresh tokens if nescessary
        if oa_client.is_token_expired(self._spotify):
            self._spotify = oa_client.refresh_access_token(self._spotify)

        # Save/return new credentials if possible
        if self._spotify:
            db_utils.spotify_credentials_upsert(app.engine,
                                                self.id,
                                                self._spotify)
            return spotipy.Spotify(auth=self._spotify['access_token'])


class Playlist(object):
    ''' Playlist object representation '''
    def __init__(self, playlist_id, title=None, duration=0, count=0):
        self.id = playlist_id
        self.title = title
        self.duration = duration
        self.count = count
