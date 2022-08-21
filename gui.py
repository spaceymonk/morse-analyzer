import os

import matplotlib.pyplot as plt
import PySimpleGUI as sg

from config import ABOUT_TEXT, DEFAULTS


# ---------------------------------------------------- Theme Setup --------------------------------------------------- #

sg.theme("DarkBlue")
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = "#1a2835"
plt.rcParams['figure.figsize'] = (11, 5.5)
plt.rcParams['font.family'] = 'sans'
plt.rcParams['font.size'] = 10.0
SMALLFONT = ("Helvitica", 10)
APPFONT = ('Helvitica', 12)
MONOSPACEFONT = ('Consolas', 12)


# -------------------------------------------------------------------------------------------------------------------- #

def create_window(filename):
    layout = generate_layout(filename)
    window = sg.Window('Morse Analyzer', layout, grab_anywhere=True, finalize=True, location=(0, 0), resizable=False,
                       font=APPFONT)
    return window


def show_about():
    sg.popup_ok(ABOUT_TEXT, title='About', icon='info', keep_on_top=True, grab_anywhere=True, font=APPFONT)


def get_filename():
    # Get the filename from the user
    filename = sg.popup_get_file('Choose an audio file', keep_on_top=True, grab_anywhere=True, location=(0, 0),
                                 font=APPFONT, file_types=(("Audio Files", "*.wav"),))
    if filename is None:
        return
    while not os.path.exists(filename):
        sg.popup_error('Please select a file!', keep_on_top=True)
        filename = sg.popup_get_file('Choose an audio file', keep_on_top=True, grab_anywhere=True, location=(0, 0),
                                     font=APPFONT)
        if filename is None:
            return
    return filename


def generate_layout(filename):
    plotting_frame = sg.Frame('Plotting', layout=[[
        sg.Column(layout=[
            [
                sg.T('Time window limits:', s=25),
                sg.Input(k='plot_time_min', s=10, default_text=DEFAULTS['plot_time_min']),
                sg.T('-'),
                sg.Input(k='plot_time_max', s=10, default_text=DEFAULTS['plot_time_max'])
            ],
            [
                sg.T('Frequency window limits:', s=25),
                sg.Input(k='plot_freq_min', s=10, default_text=DEFAULTS['plot_freq_min']),
                sg.T('-'),
                sg.Input(k='plot_freq_max', s=10, default_text=DEFAULTS['plot_freq_max'])
            ],
            [sg.CB('Show Grids', default=DEFAULTS['plot_grids'], k='plot_grids')]
        ]),
        sg.Column(layout=[
            [sg.T('', k='-COORDS-', s=20, justification='center')],
            [sg.T('', k='-VALUE-', s=20, justification='center')],
            [sg.Button('Plot', k='-PLOT-', expand_x=True)]
        ])
    ]])
    output_layout = [
        [sg.Canvas(k='-CANVAS-')],
        [sg.Column([[plotting_frame]], expand_x=True, element_justification='center', p=((5, 5), (20, 10)))]
    ]
    shortened = filename if len(filename) < 40 else '...' + filename[-37:]
    input_layout = [
        # ------------------------------------------ Filename And SR Display ----------------------------------------- #
        [sg.Frame(title='File', expand_x=True, pad=((5, 5), (0, 20)), layout=[
            [sg.T(shortened, s=40, justification='center', tooltip=filename)],
            [
                sg.T('Sample rate:'),
                sg.T('', k='-SR-', expand_x=True, justification='end')
            ]
        ])],

        # ------------------------------------------- Re-sampling Settings ------------------------------------------- #
        [sg.Frame(title='Sampling', pad=((5, 5), (0, 20)), element_justification='center', expand_x=True, layout=[
            [
                sg.T('FFT bins:',  expand_x=True),
                sg.Input(k='n_fft', s=15, justification="end", default_text=DEFAULTS['n_fft'])
            ],
            [
                sg.T('FFT bin size:'),
                sg.T('', k='-BINSIZE-', expand_x=True, justification='end')
            ],
            [
                sg.T('Window length:',  expand_x=True),
                sg.Input(k='win_length', s=15, justification="end", default_text=DEFAULTS['win_length'])
            ],
            [
                sg.T('Hop length:',  expand_x=True),
                sg.Input(k='hop_length', s=15, justification="end", default_text=DEFAULTS['hop_length'])
            ],
            [sg.Button('Render', k='-RENDER-', s=10)]
        ])],

        # ----------------------------------------- Audio Filtering Settings ----------------------------------------- #
        [sg.Frame(title='Filtering', pad=((5, 5), (0, 20)), element_justification='center', expand_x=True, layout=[
            [
                sg.CB('Threshold (dB):', expand_x=True, default=DEFAULTS['apply_threshold_db'], k='apply_threshold_db'),
                sg.Input(k='threshold_db', s=15, justification="end", default_text=DEFAULTS['threshold_db'])
            ],
            [
                sg.CB('Frequency band (Hz):',  expand_x=True, default=DEFAULTS['apply_freq_band'], k='apply_freq_band'),
                sg.Input(k='freq_band_min', s=10, justification="end", default_text=DEFAULTS['freq_band_min']),
                sg.T('-'),
                sg.Input(k='freq_band_max', s=10, justification="end", default_text=DEFAULTS['freq_band_max'])
            ],
            [
                sg.CB('Time band (s):',  expand_x=True, default=DEFAULTS['apply_time_band'], k='apply_time_band'),
                sg.Input(k='time_band_min', s=10, justification="end", default_text=DEFAULTS['time_band_min']),
                sg.T('-'),
                sg.Input(k='time_band_max', s=10, justification="end", default_text=DEFAULTS['time_band_max'])
            ],
            [sg.Button('Apply', k='-APPLY-', s=10)]
        ])],

        # ------------------------------------------- Morse Decode Display ------------------------------------------- #
        [sg.Frame(title='Decoding', pad=((5, 5), (0, 10)), expand_x=True, element_justification='center', layout=[
            [sg.Button('Solve', k='-SOLVE-', s=10)],
            [sg.Multiline(s=(40, 5), k='-ENCODED-', font=MONOSPACEFONT)],
            [sg.Button('Decode', k='-DECODE-', s=10)],
            [sg.Multiline(s=(40, 4), k='-DECODED-', font=MONOSPACEFONT)]
        ])]
    ]

    # ================================================================================================================ #
    #                                                      LAYOUT                                                      #
    # ================================================================================================================ #
    layout = [
        [sg.Menu([['&Help', ['&About::-ABOUT-']]], tearoff=False)],
        [
            sg.Column(output_layout, vertical_alignment='top', expand_y=True),
            sg.Column(input_layout, vertical_alignment='top', expand_y=True)
        ],
        [sg.StatusBar('Ready', k='-STATUS-', p=0, size=180, font=SMALLFONT)]
    ]
    return layout
