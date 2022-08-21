import numpy as np
import sklearn.cluster
import scipy.io.wavfile
import scipy.signal

from config import MORSE
from util import bin_to_freq, frames_to_time, get_domains


def load_file(filename):
    sr, y = scipy.io.wavfile.read(filename)
    if y.ndim > 1:
        y = np.mean(y, axis=1).flatten()
    y = np.interp(y, (y.min(), y.max()), (-1, 1))
    return y, sr


def get_dft(y, sr, values):
    # get stft
    n_fft = int(values['n_fft'])
    win_length = int(values['win_length'])
    hop_length = int(values['hop_length'])
    f,t, stft = scipy.signal.stft(y, sr, window='hann', nperseg=win_length, noverlap=win_length-hop_length, nfft=n_fft)

    # convert to dB
    amin = 1e-10
    top_db = 80.0
    magnitude = np.abs(stft)
    ref_value = np.max(magnitude) ** 2
    power = np.square(magnitude, out=magnitude)

    log_spec = 10.0 * np.log10(np.maximum(amin, power))
    log_spec -= 10.0 * np.log10(np.maximum(amin, ref_value))
    log_spec = np.maximum(log_spec, log_spec.max() - top_db)

    return log_spec


def tweak_dft(dft, sr, values):
    # apply threshold db filter
    if(values['apply_threshold_db']):
        threshold_db = -80 if values['threshold_db'] == '' else float(values['threshold_db'])
        dft = np.where(dft > threshold_db, dft, -80).astype(np.int8)

    boundaries = (values['time_band_min'], values['time_band_max'], values['freq_band_min'], values['freq_band_max'])
    time_domain, freq_domain = get_domains(dft.shape, sr, boundaries, values)

    # apply frequency band filter
    if values['apply_freq_band']:
        top = np.zeros((freq_domain[0], dft.shape[1]), dtype=np.int8) - 80
        bottom = np.zeros((dft.shape[0] - freq_domain[1], dft.shape[1]), dtype=np.int8) - 80
        dft = np.concatenate((top, dft[freq_domain[0]:freq_domain[1], :], bottom), axis=0)
    # apply time band filter
    if values['apply_time_band']:
        top = np.zeros((dft.shape[0], time_domain[0]), dtype=np.int8) - 80
        bottom = np.zeros((dft.shape[0], dft.shape[1] - time_domain[1]), dtype=np.int8) - 80
        dft = np.concatenate((top, dft[:, time_domain[0]:time_domain[1]], bottom), axis=1)
    # return dft
    return dft


def solve(dft, sr, values):
    interp = np.interp(dft, [np.amin(dft), np.amax(dft)], [0, 1])  # map to [0, 1]
    status = []

    # -------------------------------------------- Find Dominant Frequency ------------------------------------------- #
    dominant_freq_bin = np.argmax(np.mean(interp, axis=1), axis=0)
    status.append('Dominant frequency found between: {:.2f} Hz and {:.2f} Hz'.format(
        bin_to_freq(dominant_freq_bin, sr, values), bin_to_freq(dominant_freq_bin+1, sr, values)))

    # ----------------------------------- Find The Positions Of Rising And Falling ----------------------------------- #
    binary_data = np.where(interp[dominant_freq_bin] > 0.85, 1, 0)  # 0.85 is the threshold
    diff = np.diff(binary_data)  # find the differences between consecutive values to find the rising and falling
    rising_idx = np.nonzero(diff == 1)[0]
    falling_idx = np.nonzero(diff == -1)[0]

    # if we only observed the falling edge, we need to add the rising edge at the beginning
    if falling_idx[0] < rising_idx[0]:
        rising_idx = np.insert(rising_idx, 0, -1)

    # if value did not fell at the end, we need to add the falling edge at the end
    if rising_idx[-1] > falling_idx[-1]:
        falling_idx = np.insert(falling_idx, len(falling_idx), len(binary_data) - 1)

    on_frames = falling_idx - rising_idx  # the number of samples between rising and falling
    off_frames = rising_idx[1:] - falling_idx[:len(falling_idx)-1]  # the number of samples btwn falling and rising

    # ------------------------------------------------- Find Symbols ------------------------------------------------- #
    if len(on_frames) == 0:
        status.append('!Could not found any dash/dot symbols!')
        return '', ' | '.join(status)

    # separate symbols into dot and dash
    symbol_cluster = sklearn.cluster.KMeans(2).fit(on_frames.reshape(-1, 1))

    sorted_label_idx = np.argsort(symbol_cluster.cluster_centers_.flatten())
    dot_label = sorted_label_idx[0]
    dash_label = sorted_label_idx[1]
    status.append('Dot: {:.0f} ms, Dash: {:.0f} ms'.format(
        1000*frames_to_time(symbol_cluster.cluster_centers_.flatten()[dot_label], sr, values),
        1000*frames_to_time(symbol_cluster.cluster_centers_.flatten()[dash_label], sr, values)))

    # extract symbols
    symbols = ['.' if i == dot_label else '-' for i in symbol_cluster.labels_]

    # ------------------------------------------------- Find Spacings ------------------------------------------------ #
    if len(off_frames) == 0:
        status.append('!Could not find spacing between symbols!')
        return '', ' | '.join(status)

    # separate spacings into symbol, letter, and word lengths
    spacing_cluster = sklearn.cluster.KMeans(3).fit(off_frames.reshape(-1, 1))

    sorted_label_idx = np.argsort(spacing_cluster.cluster_centers_.flatten())
    symbol_spacing = sorted_label_idx[0]
    letter_spacing = sorted_label_idx[1]
    word_spacing = sorted_label_idx[2]

    # break into symbols
    symbol_break_idx = np.flatnonzero(spacing_cluster.labels_ != symbol_spacing) + 1
    remaining_spacings = spacing_cluster.labels_[spacing_cluster.labels_ != symbol_spacing]
    # break into words
    word_break_idx = np.flatnonzero(remaining_spacings == word_spacing) + 1

    status.append('Symbol spacing: {:.0f} ms, Letter spacing: {:.0f} ms, Word spacing: {:.0f} ms'.format(
        1000*frames_to_time(spacing_cluster.cluster_centers_.flatten()[symbol_spacing], sr, values),
        1000*frames_to_time(spacing_cluster.cluster_centers_.flatten()[letter_spacing], sr, values),
        1000*frames_to_time(spacing_cluster.cluster_centers_.flatten()[word_spacing], sr, values)))

    # --------------------------------------------------- Find Code -------------------------------------------------- #
    symbol_start_idx = [0] + symbol_break_idx.tolist()
    symbol_end_idx = symbol_break_idx.tolist() + [len(symbols)]
    letters = ["".join(symbols[i:j]) for i, j in zip(symbol_start_idx, symbol_end_idx)]

    word_start_idx = [0] + (word_break_idx).tolist()
    word_end_idx = (word_break_idx).tolist() + [len(letters)]
    words = [" ".join(letters[i:j]) for i, j in zip(word_start_idx, word_end_idx)]

    return '/'.join(words), ' | '.join(status)


def decode(encoded):
    code = encoded.strip()
    if code == '':
        return ''
    words = code.split('/')
    decoded = []
    for word in words:
        letters = word.split(' ')
        for letter in letters:
            decoded.append(MORSE[letter] if letter in MORSE else '¿')
        decoded.append(' ')
    return ''.join(decoded)
