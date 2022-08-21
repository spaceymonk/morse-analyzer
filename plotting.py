import matplotlib.pyplot as plt
import numpy as np

from util import fft_frequencies, frames_to_time, get_domains


def plot(dft, sr, values):
    fig, ax = plt.subplots()
    img = ax.imshow(dft, aspect='auto', origin='lower', interpolation="none")
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    ax.set_title('Spectrogram')
    ax.grid(values['plot_grids'])
    plt.subplots_adjust(left=0.1, right=1.05, top=0.95, bottom=0.15)

    boundaries = (values['plot_time_min'], values['plot_time_max'], values['plot_freq_min'], values['plot_freq_max'])
    time_domain, freq_domain = get_domains(dft.shape, sr, boundaries, values)

    # Handle time axis
    frame_times = frames_to_time(np.arange(dft.shape[1]), sr, values)
    x_ticks = np.linspace(time_domain[0], time_domain[1], 15, endpoint=False).astype(int)
    x_ticks_labels = [f"{x:.2f}" for x in frame_times[x_ticks]]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticks_labels, rotation=45)
    ax.set_xlabel('Time (s)')
    ax.set_xlim(time_domain)

    # Handle frequency axis
    fft_freqs = fft_frequencies(sr, values)
    y_ticks = np.linspace(freq_domain[0], freq_domain[1], 10, endpoint=False).astype(int)
    y_ticks_labels = [f"{x:.2f}" for x in fft_freqs[y_ticks]]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks_labels)
    ax.set_ylabel('Frequency (Hz)')
    ax.set_ylim(freq_domain)

    return fig, ax
