from lightfm import LightFM
import pickle
import db_utils
import scipy
import numpy as np

NUM_COMPONENTS = 30
NUM_EPOCHS = 20
MODEL_LOCATION = 'lightfm_model.pickle'


def get_interactions(engine):
    num_playlists = db_utils.playlist_max_id(engine)
    num_songs = db_utils.song_max_id(engine)
    interactions = scipy.sparse.csr_matrix((num_playlists+1, num_songs+1))
    plist_records = db_utils.get_playlist_interactions(engine)
    for r in plist_records:
        interactions[r.playlist_id, r.song_id] = 1
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
