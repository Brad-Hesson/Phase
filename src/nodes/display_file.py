import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', default='data_1568413886.hdf5')
rv = parser.parse_args()

with h5py.File(rv.file, 'r') as f:
    clock_base = f['clock_base'][()]
    close = np.array(f['close'])
    wide = np.array(f['wide'])

gain = 83

close[:, 1] *= 10e6 / gain**2
close[:, 0] -= close[0, 0]
close[:, 0] /= clock_base
wide[:, 1] *= 10e6 / gain
wide[:, 0] -= wide[0, 0]
wide[:, 0] /= clock_base

if True:
    fig = plt.figure()
    ax = fig.add_subplot(111)

    fig.show()

    ax.plot(close[:, 0].real, abs(close[:, 1]))
    ax.plot(wide[:, 0].real, abs(wide[:, 1]))

    RUN = True
    while RUN:
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            RUN = False