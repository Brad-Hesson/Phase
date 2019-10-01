import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', default='data_1569887045.hdf5')
rv = parser.parse_args()

with h5py.File(rv.file, 'r') as f:
    close_history = np.array(f['close'])
    wide_history = np.array(f['wide'])

default_gain = 49.5
g_rot = (0.977795681556585-0.20956050469803128j)

close_history[:, 1] *= 1e6 / default_gain ** 2 / g_rot
close_history[:, 0] -= close_history[0, 0]
wide_history[:, 1] *= 1e6 / default_gain
wide_history[:, 0] -= wide_history[0, 0]

fig = plt.figure()
ax_polar = fig.add_axes([0.125, 0.15, 0.35, 0.8])
ax_polar.set_xlabel('Resistive (uV)')
ax_polar.set_ylabel('Mechanical (uV)')
ax_polar.grid()
line_polar_close = ax_polar.plot([])[0]
ax_polar.set_aspect(1)
line_polar_wide = ax_polar.plot([])[0]
radius = 6 / default_gain / default_gain * 1e6
ax_polar.plot(radius * np.cos(np.linspace(0, 2*np.pi)), radius * np.sin(np.linspace(0, 2*np.pi)))

slider = Slider(fig.add_axes([0.125, 0.1, 0.35, 0.03]), 'History', 1, max(len(close_history), len(wide_history)), 1000, valstep=1)

ax_real = fig.add_subplot(222, title='Resistive')
ax_real.xaxis.set_visible(False)
ax_real.set_ylabel('uV')
line_real_close = ax_real.plot([])[0]
line_real_wide = ax_real.plot([])[0]

ax_imag = fig.add_subplot(224, sharex=ax_real, title='Mechanical')
ax_imag.set_xlabel('Minutes')
ax_imag.set_ylabel('uV')
line_imag_close = ax_imag.plot([])[0]
line_imag_wide = ax_imag.plot([])[0]
ax_real.set_xlim(-5, 0)
ax_real.set_ylim(-2500, 2500)
ax_imag.set_ylim(-2500, 2500)

fig.show()

run = True
while run:
    try:
        history = int(slider.val)
        line_polar_close.set_data(close_history[-history:, 1].real, close_history[-history:, 1].imag)
        line_polar_wide.set_data(wide_history[-history:, 1].real, wide_history[-history:, 1].imag)
        line_real_close.set_data(close_history[:, 0].real / 60., close_history[:, 1].real)
        line_imag_close.set_data(close_history[:, 0].real / 60., close_history[:, 1].imag)
        line_real_wide.set_data(wide_history[:, 0].real / 60., wide_history[:, 1].real)
        line_imag_wide.set_data(wide_history[:, 0].real / 60., wide_history[:, 1].imag)

        fig.canvas.draw()
        fig.canvas.flush_events()
    except TclError:
        run = False
