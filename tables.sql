CREATE TABLE IF NOT EXISTS users(
    id SERIAL,
    username varchar(200) NOT NULL,
    email varchar(200) NOT NULL,
    password_hash varchar(200) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS spotify_credentials(
    user_id BIGINT UNSIGNED,
    token_info TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS playlists(
    id SERIAL,
    user_id BIGINT UNSIGNED NOT NULL,
    title varchar(200),
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS songs(
    id SERIAL,
    title varchar(200),
    artist varchar(200),
    album varchar(200),
    lyrics TEXT,
    preview_url varchar(200),
    spotify_id VARCHAR(200),
    wave_info TEXT,
    pos REAL,
    neu REAL,
    neg REAL,
    compound REAL,
    duration INT,
    tempo FLOAT,
    pitch FLOAT,
    harmonic FLOAT,
    percussive FLOAT,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS playlist_entry(
    playlist_id BIGINT UNSIGNED NOT NULL,
    song_id BIGINT UNSIGNED NOT NULL,
    position BIGINT NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (playlist_id, position)
);

CREATE TABLE IF NOT EXISTS votes(
    playlist_id BIGINT UNSIGNED NOT NULL,
    position BIGINT NOT NULL,
    FOREIGN KEY (playlist_id, position) REFERENCES playlist_entry(playlist_id, position)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS keywords(
    song_id BIGINT UNSIGNED NOT NULL,
    word VARCHAR(200),
    weight DOUBLE,
    FOREIGN KEY (song_id) REFERENCES songs(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (song_id, word)
);

CREATE TABLE IF NOT EXISTS following(
    user_id BIGINT UNSIGNED,
    following_id BIGINT UNSIGNED,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (user_id, following_id)
);
