import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np

directory = '../../data/'
filename = 'SN16_cure.hdf5'

gain = 42.5
theta = -32.0


def main(rv):
    with h5py.File(rv.file, 'r') as f:
        close_history = np.array(f['close'][::1000])
        wide_history = np.array(f['wide'][::1000])

    close_history[:, 1] *= 1e6 / gain ** 2 / (np.cos(theta / 180.0 * np.pi)+np.sin(theta / 180.0 * np.pi)*1j)
    close_history[:, 0] -= close_history[0, 0]
    wide_history[:, 1] *= 1e6 / gain ** 1
    wide_history[:, 0] -= wide_history[0, 0]

    index_ratio = len(wide_history) / wide_history[-1, 0].real * 60

    plt.style.use('ggplot')
    fig = plt.figure()

    ax_polar = fig.add_subplot(121)
    ax_polar.set_xlabel('Resistive (uV)')
    ax_polar.set_ylabel('Mechanical (uV)')
    ax_polar.grid()
    line_polar_close = ax_polar.plot([])[0]
    ax_polar.set_aspect(1)
    line_polar_wide = ax_polar.plot([])[0]
    radius = 6 / gain / gain * 1e6
    ax_polar.plot(radius * np.cos(np.linspace(0, 2*np.pi)), radius * np.sin(np.linspace(0, 2*np.pi)))

    ax_real = fig.add_subplot(222, title='Resistive')
    ax_real.xaxis.set_visible(False)
    ax_real.set_ylabel('uV')
    ax_real.plot(close_history[:, 0].real / 60., close_history[:, 1].real)
    ax_real.plot(wide_history[:, 0].real / 60., wide_history[:, 1].real)

    ax_imag = fig.add_subplot(224, sharex=ax_real, title='Mechanical')
    ax_imag.set_xlabel('Minutes')
    ax_imag.set_ylabel('uV')
    ax_imag.plot(close_history[:, 0].real / 60., close_history[:, 1].imag)
    ax_imag.plot(wide_history[:, 0].real / 60., wide_history[:, 1].imag)

    fig.show()

    run = True
    while run:
        try:
            start = max(0, int(ax_real.get_xlim()[0] * index_ratio))
            end = int(ax_real.get_xlim()[1] * index_ratio)

            line_polar_close.set_data(close_history[start:end, 1].real, close_history[start:end, 1].imag)
            line_polar_wide.set_data(wide_history[start:end, 1].real, wide_history[start:end, 1].imag)

            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            run = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default=directory + filename)
    rv = parser.parse_args()
    main(rv)