import threading

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

from src.com import Message, Node

node = Node('calibration')
kill = node.kill_flag()
recv_data = node.Receiver('mfli/low_gain')
tran_calib = node.Transmitter('mfli/calibration')
node.register_node()


def t():
    global run
    raw_input()
    run = False


thread = threading.Thread(target=t)
thread.start()
run = True
data = np.zeros((0, 2), dtype=np.complex)
while run:
    data = np.concatenate((data, Message(recv_data.read()).data), axis=0)

recv_data.close()
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
tran_calib.transmit(msg)
tran_calib.close()

ax.cla()
ax.plot((data[:, 1] * const).real, (data[:, 1] * const).imag)

fig.canvas.draw()
fig.canvas.flush_events()


raw_input()
