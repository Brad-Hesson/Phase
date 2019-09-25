from _tkinter import TclError

import matplotlib.pyplot as plt
import numpy as np

from src.com import Message, Node

default_gain = 50.0


def main():
    fig = plt.figure()
    ax_polar = fig.add_subplot(121)
    ax_polar.grid()
    line_polar_close = ax_polar.plot([])[0]
    ax_polar.set_aspect(1)
    line_polar_wide = ax_polar.plot([])[0]
    radius = 6 / default_gain / default_gain * 1e6
    ax_polar.plot(radius * np.cos(np.linspace(0, 2*np.pi)), radius * np.sin(np.linspace(0, 2*np.pi)))

    ax_real = fig.add_subplot(222, title='Real')
    line_real_close = ax_real.plot([])[0]
    line_real_wide = ax_real.plot([])[0]

    ax_imag = fig.add_subplot(224, sharex=ax_real, title='Imaginary')
    line_imag_close = ax_imag.plot([])[0]
    line_imag_wide = ax_imag.plot([])[0]
    ax_real.set_xlim(-1, 0)
    ax_real.set_ylim(-9000, 9000)
    ax_imag.set_ylim(-9000, 9000)

    fig.show()

    node = Node('display')
    kill = node.kill_flag()
    sub_high_gain = node.Subscriber('mfli/high_gain')
    sub_low_gain = node.Subscriber('mfli/low_gain')
    node.register_node()

    gain_buffer = [default_gain]
    gain_buffer_length = 5000
    close_window = np.zeros((3000, 2), dtype=np.complex)
    wide_window = np.zeros((3000, 2), dtype=np.complex)
    while not kill:
        try:
            recv = []
            while len(recv) == 0:
                recv = sub_high_gain.read()
            close = Message(recv[-1]).data

            recv = []
            while len(recv) == 0:
                recv = sub_low_gain.read()
            wide = Message(recv[-1]).data

            #for c, w in zip(close[:, 1], wide[:, 1]):
            #    if abs(c) < 6 and w != 0:
            #        gain_buffer.append(c / w)
            #        gain_buffer.pop(0) if len(gain_buffer) > gain_buffer_length else None

            gain = default_gain

            close[:, 1] /= (gain * gain)
            wide[:, 1] /= gain

            close_window[1:] = close_window[:-1]
            close_window[0] = close[-1]
            wide_window[1:] = wide_window[:-1]
            wide_window[0] = wide[-1]

            line_polar_close.set_data(close[:, 1].real * 1e6, close[:, 1].imag * 1e6)
            line_polar_wide.set_linestyle('None' if abs(close[-1, 1]) < abs(6 / gain / gain) else '-')
            line_polar_wide.set_data(wide[:, 1].real * 1e6, wide[:, 1].imag * 1e6)
            line_real_close.set_data((close_window[:, 0].real - close_window[0, 0]) / 60., close_window[:, 1].real * 1e6)
            line_imag_close.set_data((close_window[:, 0].real - close_window[0, 0]) / 60., close_window[:, 1].imag * 1e6)
            line_real_wide.set_data((wide_window[:, 0].real - wide_window[0, 0]) / 60., wide_window[:, 1].real * 1e6)
            line_imag_wide.set_data((wide_window[:, 0].real - wide_window[0, 0]) / 60., wide_window[:, 1].imag * 1e6)

            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            kill = True


if __name__ == '__main__':
    main()
