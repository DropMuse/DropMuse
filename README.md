# DropMuse

## Install / Setup
1. Clone repo:

    ```
    git clone https://github.com/DropMuse/DropMuse
    cd DropMuse
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Copy `.env` template:

    ```
    cp .env.template .env
    ```

4. Add your local DB credentials to your `.env`.
5. Create the SQL tables from `tables.sql` in your database.

### Production setup

#### Database Setup
Set the following environment variables accordingly (or add to `app/.env`):
* `DB_USER` - MySQL username
* `DB_PASS` - MySQL password
* `DB_HOST` - MySQL server hostname
* `DB_PORT` - MySQL server port
* `DB_DBNAME` - MySQL database
* `DB_PREFIX` - URI scheme to use for connecting to the db. (Defaults to `mysql+pymysql://`)

Alternatively, you can set `DATABASE_URL` to specify the full URL. (Used for Heroku)

#### Spotify Setup
Set the following environment variables accordingly (or add to `app/.env`):

* `SPOTIFY_CLIENT_ID`
* `SPOTIFY_CLIENT_SECRET`

You can obtain a `CLIENT_ID` and `CLIENT_SECRET` [here](https://developer.spotify.com/my-applications/#!/applications).
Use `http://SERVER_HOST:PORT/spotify/callback` as the `Redirect URI` when setting up the app.

#### Misc

* `SERVER_NAME` - Defaults to `0.0.0.0:{PORT}`. Used to construct Spotify callback URL.
* `PORT` - Defaults to `5000`. Flask server port. Used to construct Spotify callback URL.

## Run the app

```
python run.py
```
