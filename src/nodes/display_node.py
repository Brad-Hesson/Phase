import matplotlib.pyplot as plt
import numpy as np
from _tkinter import TclError
from matplotlib.widgets import Slider
from src.com import Message, Node

gain = 49.5
max_length = 500000

close_history = np.zeros((0, 2), dtype=np.complex)
wide_history = np.zeros((0, 2), dtype=np.complex)


def main():
    global close_history
    global wide_history
    fig = plt.figure()
    ax_polar = fig.add_axes([0.125, 0.15, 0.35, 0.8])
    ax_polar.set_xlabel('Resistive (uV)')
    ax_polar.set_ylabel('Mechanical (uV)')
    ax_polar.grid()
    line_polar_close = ax_polar.plot([])[0]
    ax_polar.set_aspect(1)
    line_polar_wide = ax_polar.plot([])[0]
    radius = 6 / gain / gain * 1e6
    ax_polar.plot(radius * np.cos(np.linspace(0, 2*np.pi)), radius * np.sin(np.linspace(0, 2*np.pi)))

    slider = Slider(fig.add_axes([0.125, 0.1, 0.35, 0.03]), 'History', 1, 1000, 10, valstep=1)

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

    node = Node('display')
    kill = node.kill_flag()
    node.Receiver('mfli/high_gain', high_gain_cb)
    node.Receiver('mfli/low_gain', low_gain_cb)
    node.register_node()

    while not kill:
        try:
            history = int(slider.val)
            line_polar_close.set_data(close_history[-history:, 1].real * 1e6, close_history[-history:, 1].imag * 1e6)
            line_polar_wide.set_data(wide_history[-history:, 1].real * 1e6, wide_history[-history:, 1].imag * 1e6)
            line_real_close.set_data((close_history[:, 0].real - close_history[-1, 0]) / 60., close_history[:, 1].real * 1e6)
            line_imag_close.set_data((close_history[:, 0].real - close_history[-1, 0]) / 60., close_history[:, 1].imag * 1e6)
            line_real_wide.set_data((wide_history[:, 0].real - wide_history[-1, 0]) / 60., wide_history[:, 1].real * 1e6)
            line_imag_wide.set_data((wide_history[:, 0].real - wide_history[-1, 0]) / 60., wide_history[:, 1].imag * 1e6)

            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            kill = True


def high_gain_cb(msg):
    global close_history
    close = Message(msg).data[-1]
    close[1] /= (gain * gain * (0.977795681556585 - 0.20956050469803128j))
    close_history = np.concatenate((close_history, [close]), axis=0)
    close_history = close_history[1:] if len(close_history) > max_length else close_history


def low_gain_cb(msg):
    global wide_history
    wide = Message(msg).data[-1]
    wide[1] /= gain
    wide_history = np.concatenate((wide_history, [wide]), axis=0)
    wide_history = wide_history[1:] if len(wide_history) > max_length else wide_history


if __name__ == '__main__':
    main()
