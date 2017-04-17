import numpy as np
import librosa
import urllib


def get_audio_analysis(song_url):
    if(song_url is None):
        return None, None, None, None
    urllib.urlretrieve(song_url, "current.mp3")
    y, sr = librosa.load("./current.mp3")

    # Tempo = beats/minute
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # pitch = Frequency
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_ave = np.average(pitches)

    harm = np.sum(librosa.effects.harmonic(y))
    perc = np.sum(librosa.effects.percussive(y))

    return float(tempo), float(pitch_ave), float(harm), float(perc)
