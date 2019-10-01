import argparse
from _tkinter import TclError

import h5py
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', default='SN1_slow_ramp.hdf5')
rv = parser.parse_args()

with h5py.File(rv.file, 'r') as f:
    wide_history = np.array(f['wide'])
    temp_history = np.array(f['temp'])
    setpoint_history = np.array(f['setpoint'])

default_gain = 49.5
g_rot = (0.977795681556585-0.20956050469803128j)

wide_history[:, 1] *= 1e6 / default_gain
wide_history[:, 0] -= wide_history[0, 0]
temp_history[:, 0] -= temp_history[0, 0]
setpoint_history[:, 0] -= setpoint_history[0, 0]

fig = plt.figure()
ax = fig.add_subplot(211)
ax.plot(wide_history[:, 0].real / 60. / 60., np.abs(wide_history[:, 1] - wide_history[0, 1]))
ax2 = fig.add_subplot(212, sharex=ax)
ax2.plot(setpoint_history[:, 0] / 60. / 60., setpoint_history[:, 1])
ax2.plot(temp_history[:, 0] / 60. / 60., temp_history[:, 1])

fig.show()

run = True
while run:
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
    except TclError:
        run = False
