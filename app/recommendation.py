from lightfm import LightFM
import pickle
import db_utils
import scipy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

NUM_COMPONENTS = 30
NUM_EPOCHS = 20
MODEL_LOCATION = 'lightfm_model.pickle'


def get_interactions(engine):
    num_playlists = db_utils.playlist_max_id(engine)
    num_songs = db_utils.song_max_id(engine)
    interactions = scipy.sparse.csr_matrix((num_playlists+1, num_songs+1))
    plist_records = db_utils.get_playlist_interactions(engine)
    for r in plist_records:
        interaction_value = 2 if r.vote else 1
        interactions[r.playlist_id, r.song_id] = interaction_value
    return interactions


def get_item_features(engine):
    sentiments = db_utils.song_sentiments(engine)
    num_songs = db_utils.song_max_id(engine)
    item_features = scipy.sparse.csr_matrix((num_songs+1, 3))
    for idx, s in enumerate(sentiments):
        item_features[idx] = np.array([s['pos'], s['neu'], s['neg']])
    return item_features


def train_model(engine):
    '''
    interactions is of:
      shape: (num_users, num_items)
      format: 1 if positive interaction, -1 if negative interaciton
    item_features is of:
      shape: (num_items, num_features)
      format: [pos_sent, neu_sent, neg_sent]
    '''
    model = load_model()
    interactions = get_interactions(engine)
    item_features = get_item_features(engine)

    model.fit(interactions,
              item_features=item_features,
              epochs=NUM_EPOCHS)

    dump_model(model)
    return model


def get_recommendations(engine, playlist_id):
    model = train_model(engine)
    item_features = get_item_features(engine)
    num_items = item_features.shape[0]
    predictions = model.predict(playlist_id,
                                np.arange(num_items),
                                item_features=item_features)
    return [int(i) for i in np.argsort(-predictions)]


def load_model():
    '''
    Loads LightFM model from file
    Returns empty model if no pickled model found
    '''
    try:
        with open(MODEL_LOCATION, 'rb') as f:
            return pickle.load(f)
    except IOError:
        return LightFM(loss='warp',
                       no_components=NUM_COMPONENTS)


def dump_model(model):
    '''
    Saves LightFM model to file
    '''
    with open(MODEL_LOCATION, 'wb') as f:
        pickle.dump(model, f)


def extract_keywords():
    songs = db_utils.song_lyrics(engine)
    song_indices = {i: s.id for i, s in enumerate(songs)}
    lyrics = [s.lyrics for s in songs]
    tfidf = TfidfVectorizer(stop_words='english',
                            max_df=0.7)
    tfidf_mat = tfidf.fit_transform(lyrics).toarray()
    features = tfidf.get_feature_names()
    keywords = {}
    for idx, l in enumerate(tfidf_mat):
        keywords[song_indices[idx]] = [(features[x], l[x]) for x in (-l).argsort()][:10]
    for songid, word_arr in keywords.items():
        print "inserting: %s" % songid
        for kw in word_arr:
            db_utils.add_song_keyword(engine, songid, kw[0], float(kw[1]))
