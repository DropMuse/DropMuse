from lightfm import LightFM
import pickle
import db_utils
import scipy
import numpy as np
import numpy.linalg as la
from nltk.tokenize import word_tokenize, RegexpTokenizer

regex_tokenizer = RegexpTokenizer(r'\w+')

NUM_COMPONENTS = 30
NUM_EPOCHS = 20
MODEL_LOCATION = 'lightfm_model.pickle'


def get_interactions(engine):
    num_playlists = db_utils.playlist_max_id(engine)
    num_songs = db_utils.song_max_id(engine)
    interactions = scipy.sparse.lil_matrix((num_playlists+1, num_songs+1))
    plist_records = db_utils.get_playlist_interactions(engine)
    for r in plist_records:
        interaction_value = 2 if r.vote else 1
        interactions[r.playlist_id, r.song_id] = interaction_value
    return interactions


def get_audio_analysis_features(engine):
    features = db_utils.song_audio_features(engine)
    num_songs = db_utils.song_max_id(engine)
    feature_mat = scipy.sparse.lil_matrix((num_songs+1, 4))
    for s in features:
        pitch = s.pi or 0
        harmonic = s.h or 0
        percussive = s.pe or 0
        temp = s.t or 0
        feature_mat[s.id] = np.array([pitch, harmonic, percussive, temp])
    return feature_mat


def artist_matrix(engine):
    '''
    Returns matrix of shape (num_songs, num_artists)
    '''
    songs = db_utils.song_artists(engine)
    num_songs = db_utils.song_max_id(engine)
    artists = set(s.artist for s in songs)
    artist_indices = {s: i for i, s in enumerate(artists)}
    artist_mat = scipy.sparse.lil_matrix((num_songs+1, len(artists)))
    for s in songs:
        artist_mat[s.id, artist_indices[s.artist]] = 1
    return artist_mat


def get_item_features(engine):
    '''
    - Resultant matrix is of shape: (num_songs, num_features)
    - Matrix can be indexed as (song_id, feature_idx)
    '''
    sentiments = db_utils.song_sentiments(engine)
    num_songs = db_utils.song_max_id(engine)
    item_features = scipy.sparse.lil_matrix((num_songs+1, 3))
    for s in sentiments:
        pos = s.pos or 0
        neu = s.neu or 0
        neg = s.neg or 0
        sent_arr = np.array([pos, neu, neg])
        norm = la.norm(sent_arr)
        if norm > 0:
            item_features[s.id] = sent_arr / norm
    keywords = keyword_sparse_matrix(engine)
    artists = artist_matrix(engine)
    audio = get_audio_analysis_features(engine)
    results = scipy.sparse.hstack([item_features, keywords, artists, audio])
    return results


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


def keyword_sparse_matrix(engine):
    keyword_list = list(db_utils.all_keywords(engine))
    keyword_dict = {}
    curr_idx = 0
    for k in keyword_list:
        if k.word not in keyword_dict:
            keyword_dict[k.word] = curr_idx
            curr_idx += 1
    num_songs = db_utils.song_max_id(engine)
    keyword_mat = scipy.sparse.lil_matrix((num_songs + 1, curr_idx + 1))
    for k in keyword_list:
        keyword_mat[k.song_id, keyword_dict[k.word]] = k.weight

    # Normalize rows
    for r in range(keyword_mat.shape[0]):
        norm = la.norm(keyword_mat.getrow(r).todense())
        if norm > 0:
            keyword_mat[r] = keyword_mat.getrow(r) / norm
    return keyword_mat


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


def word_tokenize_no_punct(sent):
    tokens = regex_tokenizer.tokenize(sent)
    return [w for w in tokens if w.isalpha()]


def songs_to_vocab(songs):
    vocab = set()
    for s in songs:
        if not s.lyrics:
            continue
        sent_vocab = set(word_tokenize_no_punct(s.lyrics))
        vocab |= sent_vocab
    return list(vocab)


def tf(mat, doc, term):
    s = np.sum(mat.getrow(doc).todense())
    if s != 0:
        return mat[doc, term] / float(s)
    return 0


def idf(mat, term):
    s = mat.getcol(term).nnz
    if s != 0:
        return mat.shape[0] / float(s)
    return 0


def extract_keywords(engine):
    '''
    - Constructs a TFIDF of all lyrics of all songs
    - Extracts the most meaningful keywords of each song
    - Updates the keyword table accordingly
    '''
    songs = db_utils.song_lyrics(engine)
    # lyrics = [s.lyrics if s.lyrics else "" for s in songs]
    # tfidf = TfidfVectorizer(stop_words='english',
    #                         max_df=0.7)
    # tfidf_mat = tfidf.fit_transform(lyrics).toarray()

    vocab = songs_to_vocab(songs)
    w_indices = {k: idx for idx, k in enumerate(vocab)}

    # matrix
    # (word_idx, doc_idx) => word_doc_count
    matrix = scipy.sparse.lil_matrix((len(songs), len(vocab)))
    for i, s in enumerate(songs):
        if not s.lyrics:
            continue
        for w in word_tokenize_no_punct(s.lyrics):
            matrix[i, w_indices[w]] += 1

    # tfidf
    # (word_idx, doc_idx) => word_doc_tfidf_score
    tfidf = scipy.sparse.lil_matrix((len(songs), len(vocab)))
    nzx, nzy = matrix.nonzero()
    for i in range(len(nzx)):
        doc_idx, term_idx = nzx[i], nzy[i]
        term_freq = tf(matrix, doc_idx, term_idx)
        inv_doc_freq = idf(matrix, term_idx)
        tfidf[doc_idx, term_idx] = term_freq * inv_doc_freq

    db_utils.delete_all_keywords(engine)
    for i in range(len(songs)):
        max_indices = (-tfidf.getrow(i).toarray()[0]).argsort()[:10]
        song_id = songs[i].id
        for term_idx in max_indices:
            if tfidf[i, term_idx] == 0:
                continue
            kw_str = vocab[int(term_idx)]
            kw_weight = tfidf[i, term_idx]
            db_utils.add_song_keyword(engine,
                                      song_id,
                                      kw_str,
                                      float(kw_weight))


def similar_songs(engine, song_id, num_results=5):
    '''
    - Returns song most similar to the given song using cosine similarity
    '''
    features = get_item_features(engine)
    sample_v = np.array(features.getrow(song_id).todense())
    sample_norm = la.norm(sample_v)
    cos_diffs = []
    for i in range(features.shape[0]):
        test_v = features.getrow(i).todense().T
        norm = sample_norm * la.norm(test_v)
        cos_diffs.append(np.dot(sample_v, test_v) / norm if norm != 0 else 0)
    most_similar = np.argsort(-np.array(cos_diffs))
    similar_ids = [int(i) for i in most_similar if i != song_id][:5]
    return similar_ids
