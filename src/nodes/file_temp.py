import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np

filename = 'SN1_slow_ramp.hdf5'
start = 12000
end = -181000
step = 1000


def main(rv):
    with h5py.File(rv.file, 'r') as f:
        wide_history = np.array(f['wide'][start:end:step])
        temp_history = np.array(f['temp'][start:end:step])
        setpoint_history = np.array(f['setpoint'][start:end:step])

    default_gain = 49.5
    g_rot = (0.977795681556585-0.20956050469803128j)

    wide_history[:, 1] *= 1e6 / default_gain
    wide_history[:, 0] -= wide_history[0, 0]
    temp_history[:, 0] -= temp_history[0, 0]
    setpoint_history[:, 0] -= setpoint_history[0, 0]

    fig = plt.figure()

    ax_b = fig.add_subplot(222, title='Balance vs. Time')
    ax_b.xaxis.set_visible(False)
    ax_b.set_ylabel('Imbalance (uV)')
    ax_b.plot(wide_history[:, 0].real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).real)
    ax_b.plot(wide_history[:, 0].real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).imag)

    ax_t = fig.add_subplot(224, sharex=ax_b, title='Temperature vs. Time')
    ax_t.set_ylabel('Temperature (C)')
    ax_t.set_xlabel('Time (h)')
    ax_t.plot(setpoint_history[:, 0] / 60. / 60., setpoint_history[:, 1], 'g-')
    ax_t.plot(temp_history[:, 0] / 60. / 60., temp_history[:, 1], 'r-')

    ax_bt = fig.add_subplot(121, title='Balance vs. Temperature')
    ax_bt.plot(temp_history[:, 1], wide_history[:, 1].real - wide_history[0, 1].real)
    ax_bt.plot(temp_history[:, 1], wide_history[:, 1].imag - wide_history[0, 1].imag)
    ax_bt.annotate("    Start", (25, 0))
    ax_bt.annotate("    End", (25, wide_history[-1, 1].real - wide_history[0, 1].real))
    ax_bt.annotate("    End", (25, wide_history[-1, 1].imag - wide_history[0, 1].imag))

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
    parser.add_argument('--file', '-f', default=filename)
    rv = parser.parse_args()
    main(rv)
