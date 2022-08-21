import numpy as np


def frames_to_samples(f, values):
    offset = int(int(values['n_fft']) // 2)
    return (np.asanyarray(f) * int(values['hop_length']) + offset).astype(int)


def samples_to_frames(s, values):
    offset = int(int(values['n_fft']) // 2)
    return np.floor((np.asanyarray(s) - offset) // int(values['hop_length'])).astype(int)


def samples_to_time(s, sr):
    return np.asanyarray(s) / float(sr)


def time_to_samples(t, sr):
    return (np.asanyarray(t) * sr).astype(int)


def frames_to_time(f, sr, values):
    samples = frames_to_samples(f, values)
    return samples_to_time(samples, sr)


def time_to_frames(t, sr, values):
    samples = time_to_samples(t, sr)
    return samples_to_frames(samples, values)


def fft_frequencies(sr, values):
    return np.fft.rfftfreq(n=int(values['n_fft']), d=1.0 / sr)


def freq_to_bin(f, sr, values):
    return int(f / get_bin_size(sr, values))


def get_bin_size(sr, values):
    return sr / int(values['n_fft'])


def bin_to_freq(f, sr, values):
    return f * get_bin_size(sr, values)


def get_domains(shape, sr, boundaries, values):
    # time domain
    if boundaries[0] == '':
        time_min = 0
    else:
        in_time_min = float(boundaries[0])
        time_min = max(0, time_to_frames(in_time_min, sr, values))
    if boundaries[1] == '':
        time_max = shape[1]
    else:
        in_time_max = float(boundaries[1])
        time_max = min(shape[1], time_to_frames(in_time_max, sr, values))

    # frequency domain
    if boundaries[2] == '':
        freq_min = 0
    else:
        in_freq_min = float(boundaries[2])
        freq_min = max(0, freq_to_bin(in_freq_min, sr, values))
    if boundaries[3] == '':
        freq_max = shape[0]
    else:
        in_freq_max = float(boundaries[3])
        freq_max = min(shape[0], freq_to_bin(in_freq_max, sr, values))

    return ((time_min, time_max), (freq_min, freq_max))
