ABOUT_TEXT = """Morse Analyzer v0.1.0

This program is written by Berktug Kaan Ozkan.

Please visit project's website for more information, how to use etc.:

My GitHub: https://github.com/spaceymonk
Project's Source: https://github.com/spaceymonk/morse-analyzer

Note: this program is lack of proper exception handling / input validation. Please make sure you have a valid inputs.
"""

DEFAULTS = {
    'n_fft': '1024',
    'win_length': '512',
    'hop_length': '256',
    'apply_threshold_db': False,
    'apply_freq_band': False,
    'apply_time_band': False,
    'threshold_db': '-80',
    'freq_band_min': '',
    'freq_band_max': '',
    'time_band_min': '',
    'time_band_max': '',
    'plot_time_min': '',
    'plot_time_max': '',
    'plot_freq_min': '',
    'plot_freq_max': '',
    'plot_grids': False,
    'dot_length': '',
    'dash_length': '',
    'letter_spacing': '',
    'word_spacing': ''
}

MORSE = {
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    ".-.-.-": ".",
    "--..--": ",",
    "..--..": "?",
    ".----.": "'",
    "-.-.--": "!",
    "-..-.": "/",
    "-.--.": "(",
    "-.--.-": ")",
    ".-...": "&",
    "---...": ":",
    "-.-.-.": ";",
    "-...-": "=",
    ".-.-.": "+",
    "-....-": "-",
    "..--.-": "_",
    ".-..-.": "\"",
    "..-...": "^",
    "...-..-": "$",
    ".--.-.": "@"
}
