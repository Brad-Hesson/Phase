from _tkinter import TclError

import matplotlib.pyplot as plt
import numpy as np

from src.com import Node, Message

max_length = 500000


def main():
    node = Node('temp_display')
    sub_temp = node.Subscriber('watlow/temp')
    sub_power = node.Subscriber('watlow/power')
    sub_set = node.Subscriber('watlow/setpoint')
    kill_flag = node.kill_flag()
    node.register_node()

    fig = plt.figure()
    ax_t = fig.add_subplot(211)
    ax_t.set_ylim(0, 130)
    ax_t.set_xlim(-1, 0)
    line_temp = ax_t.plot([])[0]
    line_set = ax_t.plot([])[0]
    ax_p = fig.add_subplot(212, sharex=ax_t)
    ax_p.set_ylim(0, 100)
    ax_p.set_xlim(-1, 0)
    line_power = ax_p.plot([])[0]
    fig.show()

    temp_history = np.zeros((0, 2))
    power_history = np.zeros((0, 2))
    set_history = np.zeros((0, 2))

    while not kill_flag:
        try:
            recv = []
            while len(recv) == 0:
                recv = sub_temp.read()
            temp = Message(recv[-1]).data
            recv = []
            while len(recv) == 0:
                recv = sub_power.read()
            power = Message(recv[-1]).data
            recv = []
            while len(recv) == 0:
                recv = sub_set.read()
            set_ = Message(recv[-1]).data

            temp_history = np.concatenate((temp_history, [temp]))
            power_history = np.concatenate((power_history, [power]))
            set_history = np.concatenate((set_history, [set_]))

            temp_history = temp_history[1:] if len(temp_history) > max_length else temp_history
            power_history = power_history[1:] if len(power_history) > max_length else power_history
            set_history = set_history[1:] if len(set_history) > max_length else set_history

            line_temp.set_data((temp_history[:, 0] - temp_history[-1, 0]) / 60.0, temp_history[:, 1])
            line_set.set_data((set_history[:, 0] - set_history[-1, 0]) / 60.0, set_history[:, 1])
            line_power.set_data((power_history[:, 0] - power_history[-1, 0]) / 60.0, power_history[:, 1])

            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            kill_flag = True


if __name__ == '__main__':
    main()
