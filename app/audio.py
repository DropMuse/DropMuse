import numpy as np
import librosa
from six.moves.urllib.request import urlretrieve


def audio_fingerprint(y):
    return np.average(y ** 2) * 100


def get_audio_analysis(song_url):
    if(song_url is None):
        return None, None, None, None, None
    urlretrieve(song_url, "current.mp3")
    y, sr = librosa.load("./current.mp3")

    # Tempo = beats/minute
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # pitch = Frequency
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_ave = np.average(pitches)

    json = {'sound_wave': y.tolist(), 'pitch': pitches.tolist()}
    y_harm, y_per = librosa.effects.hpss(y)
    harm, perc = audio_fingerprint(y_harm), audio_fingerprint(y_per)

    return float(tempo), float(pitch_ave), float(harm), float(perc), str(json)
