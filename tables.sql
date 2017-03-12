CREATE TABLE IF NOT EXISTS users(
    id BIGINT NOT NULL AUTO_INCREMENT,
    username varchar(200) NOT NULL,
    email varchar(200) NOT NULL,
    password_hash varchar(200) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS playlists(
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title varchar(200),
    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS songs(
    id BIGINT NOT NULL AUTO_INCREMENT,
    title varchar(200),
    artist varchar(200),
    album varchar(200),
    lyrics LONGTEXT,
    external_url varchar(200),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS playlist_entry(
    playlist_id BIGINT NOT NULL,
    song_id BIGINT NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
);

CREATE TABLE IF NOT EXISTS votes(
    playlist_id BIGINT NOT NULL,
    song_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
