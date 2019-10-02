import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np

directory = '../../data/'
filename = 'SN1_slow_ramp_2.hdf5'

start = 0
end = -1
step = 1000

default_gain = 49.5
g_rot = (0.977795681556585 - 0.20956050469803128j)

axis_font = 15
title_font = 18
tick_font = 12


def main(rv):
    with h5py.File(rv.file, 'r') as f:
        wide_history = np.array(f['wide'][start:end:step])
        temp_history = np.array(f['temp'][start:end:step])
        setpoint_history = np.array(f['setpoint'][start:end:step])

    wide_history[:, 1] *= 1e6 / default_gain
    wide_history[:, 0] -= wide_history[0, 0]
    temp_history[:, 0] -= temp_history[0, 0]
    setpoint_history[:, 0] -= setpoint_history[0, 0]

    plt.style.use('ggplot')
    fig = plt.figure()
    fig.suptitle('12 hour Temperature Cycle', fontsize=title_font)

    ax_b = fig.add_subplot(222)
    ax_b.set_title('Balance vs. Time', fontsize=title_font)
    ax_b.set_ylabel('Imbalance (uV)', fontsize=axis_font)
    ax_b.tick_params(labelsize=tick_font)
    ax_b.plot(wide_history[:, 0].real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).real, label='Demod X')
    ax_b.plot(wide_history[:, 0].real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).imag, label='Demod Y')
    ax_b.legend()

    ax_t = fig.add_subplot(224, sharex=ax_b)
    ax_t.set_title('Temperature vs. Time', fontsize=title_font)
    ax_t.set_ylabel('Temperature (C)', fontsize=axis_font)
    ax_t.set_xlabel('Time (h)', fontsize=axis_font)
    ax_t.tick_params(labelsize=tick_font)
    ax_t.plot(setpoint_history[:, 0] / 60. / 60., setpoint_history[:, 1], 'g-', label='Setpoint')
    ax_t.plot(temp_history[:, 0] / 60. / 60., temp_history[:, 1], 'r-', label='Temperature')
    ax_t.legend()

    ax_bt = fig.add_subplot(121)
    ax_bt.set_title('Balance vs. Temperature', fontsize=title_font)
    ax_bt.set_ylabel('Imbalance (uV)', fontsize=axis_font)
    ax_bt.set_xlabel('Temperature (C)', fontsize=axis_font)
    ax_bt.tick_params(labelsize=tick_font)
    ax_bt.plot(temp_history[:, 1], wide_history[:, 1].real - wide_history[0, 1].real, label='Demod X')
    ax_bt.plot(temp_history[:, 1], wide_history[:, 1].imag - wide_history[0, 1].imag, label='Demod Y')
    ax_bt.annotate('', xy=(25, 0), arrowprops=dict(arrowstyle='->'))
    ax_bt.legend()
    # ax_bt.annotate("    Start", (25, 0))
    # ax_bt.annotate("    End", (25, wide_history[-1, 1].real - wide_history[0, 1].real))
    # ax_bt.annotate("    End", (25, wide_history[-1, 1].imag - wide_history[0, 1].imag))

    fig.show()

    run = True
    while run:
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            run = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default=directory + filename)
    rv = parser.parse_args()
    main(rv)
