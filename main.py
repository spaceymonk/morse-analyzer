import traceback

import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import morse
from config import DEFAULTS
from gui import create_window, get_filename, show_about
from plotting import plot
from util import bin_to_freq, frames_to_time, get_bin_size


# ------------------------------------------------- Helper Functions ------------------------------------------------- #

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def setup_interactions(figure, dft, sr, values, window):
    def notify_mouse_move(event):
        if event.xdata is not None and event.ydata is not None and int(event.ydata) < dft.shape[0]:
            coords = f"{frames_to_time(event.xdata, sr, values):.4f} s  {bin_to_freq(int(event.ydata), sr, values):.2f} Hz"
            window['-COORDS-'].update(coords)
            window['-VALUE-'].update(f"{dft[int(event.ydata)][int(event.xdata)]:.2f} dB")
    figure.canvas.mpl_connect('motion_notify_event', notify_mouse_move)


# ---------------------------------------------------- Event Loop ---------------------------------------------------- #

def event_loop(window):
    try:
        # Load the audio file
        y, sr = morse.load_file(filename)
        window['-SR-'].update(f"{sr} Hz")
        dft = morse.get_dft(y, sr, DEFAULTS)
        bin_size = get_bin_size(sr, DEFAULTS)
        window['-BINSIZE-'].update(f"{bin_size:.2f} Hz")
        # Plot the spectrogram
        fig, ax = plot(dft, sr, DEFAULTS)
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
        setup_interactions(fig, dft, sr, DEFAULTS, window)
        # Wait for the user interaction
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == "-RENDER-":
                window['-STATUS-'].update("Rendering...")
                dft = morse.get_dft(y, sr, values)
                bin_size = get_bin_size(sr, values)
                window['-BINSIZE-'].update(f"{bin_size:.2f} Hz")
                window['-STATUS-'].update('Rendered')
            elif event == "-APPLY-":
                window['-STATUS-'].update("Applying...")
                dft = morse.tweak_dft(dft, sr, values)
                window['-STATUS-'].update(value='Filters applied')
            elif event == "-DECODE-":
                window['-DECODED-'].update(morse.decode(values['-ENCODED-']))
            elif event == "-SOLVE-":
                window['-STATUS-'].update("Solving...")
                code, status = morse.solve(dft, sr, values)
                window['-STATUS-'].update(status)
                window['-ENCODED-'].update(code)
                window.refresh()
            elif event == 'About::-ABOUT-':
                show_about()

            if event in ("-PLOT-", "-RENDER-", "-APPLY-"):
                plt.close('all')
                fig_canvas_agg.get_tk_widget().forget()
                fig, ax = plot(dft, sr, values)
                fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
                setup_interactions(fig, dft, sr, values, window)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        sg.Print('An error occurred.  Details:', e, tb, blocking=True)
    finally:
        window.close()


# ------------------------------------------------------ Driver ------------------------------------------------------ #

if __name__ == '__main__':
    filename = get_filename()
    if filename != None:
        # Create the window
        window = create_window(filename)
        # Run the main loop
        event_loop(window)
