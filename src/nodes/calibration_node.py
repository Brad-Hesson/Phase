import threading

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

from src.com import Message, Node

node = Node('calibration')
kill = node.kill_flag()
sub_data = node.Subscriber('mfli/low_gain')
pub_calib = node.Publisher('mfli/calibration')
node.register_node()


def t():
    global run
    raw_input()
    run = False


thread = threading.Thread(target=t)
thread.start()
run = True
data = np.zeros((0, 2), dtype=np.complex)
print('push enter to review')
while run:
    for window in sub_data.read():
        data = np.concatenate((data, Message(window).data), axis=0)

slope, intercept = linregress(data[:, 1].real, data[:, 1].imag)[0:2]
x_data = np.array([min(data[:, 1].real), max(data[:, 1].real)])

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(data[:, 1].real, data[:, 1].imag)
ax.plot(x_data, slope * x_data + intercept)
fig.show()
fig.canvas.draw()
fig.canvas.flush_events()

const = np.complex(1, slope)
const = abs(const) / const
print(np.arctan(const.imag / const.real) / np.pi * 180.)

raw_input()

msg = Message()
msg.data = const
pub_calib.publish(msg)

ax.cla()
ax.plot((data[:, 1] * const).real, (data[:, 1] * const).imag)

fig.canvas.draw()
fig.canvas.flush_events()


raw_input()
