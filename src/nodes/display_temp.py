from _tkinter import TclError

import matplotlib.pyplot as plt
import numpy as np

from src.com import Node, Message

max_length = 50000

gain = 42.5

axis_font = 15
title_font = 18
tick_font = 12


def main():
    node = Node('temp_display')
    sub_wide = node.Subscriber('mfli/low_gain')
    sub_temp = node.Subscriber('watlow/temp')
    sub_set = node.Subscriber('watlow/setpoint')
    kill_flag = node.kill_flag()
    node.register_node()

    temp_history = np.zeros((0, 2))
    setpoint_history = np.zeros((0, 2))
    wide_history = np.zeros((0, 2))

    plt.style.use('ggplot')
    fig = plt.figure()
    fig.suptitle('12 hour Temperature Cycle', fontsize=title_font)

    ax_b = fig.add_subplot(222)
    ax_b.set_title('Balance vs. Time', fontsize=title_font)
    ax_b.set_ylabel('Imbalance (uV)', fontsize=axis_font)
    ax_b.tick_params(labelsize=tick_font)
    l_rbal = ax_b.plot([], label='Demod X')[0]
    l_ibal = ax_b.plot([], label='Demod Y')[0]
    ax_b.legend()

    ax_t = fig.add_subplot(224, sharex=ax_b)
    ax_t.set_title('Temperature vs. Time', fontsize=title_font)
    ax_t.set_ylabel('Temperature (C)', fontsize=axis_font)
    ax_t.set_xlabel('Time (h)', fontsize=axis_font)
    ax_t.tick_params(labelsize=tick_font)
    l_set = ax_t.plot([], 'g-', label='Setpoint')[0]
    l_temp = ax_t.plot([], 'r-', label='Temperature')[0]
    ax_t.legend()

    ax_bt = fig.add_subplot(121)
    ax_bt.set_title('Balance vs. Temperature', fontsize=title_font)
    ax_bt.set_ylabel('Imbalance (uV)', fontsize=axis_font)
    ax_bt.set_xlabel('Temperature (C)', fontsize=axis_font)
    ax_bt.tick_params(labelsize=tick_font)
    l_xdemod = ax_bt.plot([], label='Demod X')[0]
    l_ydemod = ax_bt.plot([], label='Demod Y')[0]
    ax_bt.annotate('', xy=(25, 0), arrowprops=dict(arrowstyle='->'))
    ax_bt.legend()

    fig.show()

    while not kill_flag:
        try:
            recv = []
            while len(recv) == 0:
                recv = sub_temp.read()
            temp = Message(recv[-1]).data
            recv = []
            while len(recv) == 0:
                recv = sub_wide.read()
            wide = Message(recv[-1]).data[-1]
            recv = []
            while len(recv) == 0:
                recv = sub_set.read()
            set_ = Message(recv[-1]).data

            wide[1] /= gain

            temp_history = np.concatenate((temp_history, [temp]))
            wide_history = np.concatenate((wide_history, [wide]))
            setpoint_history = np.concatenate((setpoint_history, [set_]))

            temp_history = temp_history[1:] if len(temp_history) > max_length else temp_history
            wide_history = wide_history[1:] if len(wide_history) > max_length else wide_history
            setpoint_history = setpoint_history[1:] if len(setpoint_history) > max_length else setpoint_history

            l_rbal.set_data((wide_history[:, 0] - wide_history[-1, 0]).real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).real)
            l_ibal.set_data((wide_history[:, 0] - wide_history[-1, 0]).real / 60. / 60., (wide_history[:, 1] - wide_history[0, 1]).imag)
            l_set.set_data((setpoint_history[:, 0] - setpoint_history[-1, 0]) / 60. / 60., setpoint_history[:, 1])
            l_temp.set_data((temp_history[:, 0] - temp_history[-1, 0]) / 60. / 60., temp_history[:, 1])
            l_xdemod.set_data(temp_history[:, 1], wide_history[:, 1].real - wide_history[0, 1].real)
            l_ydemod.set_data(temp_history[:, 1], wide_history[:, 1].imag - wide_history[0, 1].imag)

            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            kill_flag = True


if __name__ == '__main__':
    main()
