import numpy as np
import librosa
from six.moves.urllib.request import urlretrieve


def audio_fingerprint(y):
    return np.average(y ** 2) * 100


def extract_max(pitches, magnitudes, shape):
    new_pitches = []
    new_magnitudes = []
    for i in range(0, shape[1]):
        new_pitches.append(float(np.max(pitches[:, i])))
        new_magnitudes.append(float(np.max(magnitudes[:, i])))
    return (new_pitches, new_magnitudes)


def get_audio_analysis(song_url):
    if(song_url is None):
        return None, None, None, None, None
    urlretrieve(song_url, "current.mp3")
    y, sr = librosa.load("./current.mp3")

    # Tempo = beats/minute
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # pitch = Frequency
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr,
                                           fmax=1000, hop_length=1000)

    pitches, magnitudes = extract_max(pitches, magnitudes, pitches.shape)
    y[abs(y) < 10**-2] = 0
    y = np.trim_zeros(y)

    json = {
        'sound_wave': np.array(y[:len(pitches)]).tolist(),
        'pitch': pitches
    }
    y_harm, y_per = librosa.effects.hpss(y)
    harm, perc = audio_fingerprint(y_harm), audio_fingerprint(y_per)
    pitch_ave = np.average(pitches)
    return float(tempo), float(pitch_ave), float(harm), float(perc), json
