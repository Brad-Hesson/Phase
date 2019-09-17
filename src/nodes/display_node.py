from _tkinter import TclError

import matplotlib.pyplot as plt
import numpy as np
import zmq

from src.com import MFLIMessage, SUB_ADDR

default_gain = 83.7


def main():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid()
    lc = ax.plot([])[0]
    ax.set_aspect(1)
    lw = ax.plot([])[0]
    radius = 6 / default_gain / default_gain * 10e6
    ax.plot(radius * np.cos(np.linspace(0, 2*np.pi)), radius * np.sin(np.linspace(0, 2*np.pi)))
    fig.show()

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(SUB_ADDR)
    socket.setsockopt(zmq.SUBSCRIBE, 'mfli_node')

    gain_buffer = [default_gain]
    gain_buffer_length = 5000
    run = True
    while run:
        try:
            msg = MFLIMessage(socket.recv().split(' ', 1)[1])

            close = msg.data_high_gain
            wide = msg.data_low_gain

            for c, w in zip(close[:, 1], wide[:, 1]):
                if abs(c) < 6 and w != 0:
                    gain_buffer.append(c / w)
                    gain_buffer.pop(0) if len(gain_buffer) > gain_buffer_length else None

            gain = np.sum(gain_buffer) / len(gain_buffer)

            close[:, 1] /= (gain * gain)
            wide[:, 1] /= gain

            lc.set_data(close[:, 1].real * 10e6, close[:, 1].imag * 10e6)
            lw.set_linestyle('None' if abs(close[-1, 1]) < abs(6 / gain / gain) else '-')
            lw.set_data(wide[:, 1].real * 10e6, wide[:, 1].imag * 10e6)
            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            run = False


if __name__ == '__main__':
    main()
