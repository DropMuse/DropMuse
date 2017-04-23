import numpy as np
import librosa
from six.moves.urllib.request import urlretrieve


def audio_fingerprint(y):
    return np.average(y ** 2) * 100

def extract_max(pitches,magnitudes, shape):
    new_pitches = []
    new_magnitudes = []
    for i in range(0, shape[1]):
        new_pitches.append(np.max(pitches[:,i]))
        new_magnitudes.append(np.max(magnitudes[:,i]))
    return (new_pitches,new_magnitudes)

def smooth(x,window_len=11,window='hanning'):
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError #"Window is on of flat, hanning, hamming, bartlett, blackman"
        s=numpy.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=numpy.ones(window_len,'d')
        else:
                w=eval('numpy.'+window+'(window_len)')
        y=numpy.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]



def get_audio_analysis(song_url):
    if(song_url is None):
        return None, None, None, None, None
    urlretrieve(song_url, "current.mp3")
    y, sr = librosa.load("./current.mp3")

    # Tempo = beats/minute
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # pitch = Frequency
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmax=1000, hop_length=1000)

    pitches, magnitudes = extract_max(pitches, magnitudes, pitches.shape)

    json = {'sound_wave': y[:len(pitches)], 'pitch': pitches}
    y_harm, y_per = librosa.effects.hpss(y)
    harm, perc = audio_fingerprint(y_harm), audio_fingerprint(y_per)
    pitch_ave = np.average(pitches)
    return float(tempo), float(pitch_ave), float(harm), float(perc), str(json)
