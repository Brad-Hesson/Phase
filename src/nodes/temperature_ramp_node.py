import time

import numpy as np

from src.com import Message, Node


def main():
    node = Node('temperature_ramp')
    pub_setpoint = node.Publisher('watlow/set_setpoint')
    kill_flag = node.kill_flag()
    node.register_node()

    ramp_time = lambda t: [t, 1, t, 1]
    ramp_temp = lambda T: [T, T, 25, 25]
    # ----------Program----------
    times = [0] + ramp_time(6)*3
    temps = [25] + ramp_temp(85)*3
    # ---------------------------
    times = np.cumsum(times)
    profile = lambda t: np.interp(t / 60. / 60., times, temps)

    msg = Message()
    start = time.time()

    while not kill_flag:
        now = time.time() - start
        msg.data = profile(now)
        pub_setpoint.publish(msg)


if __name__ == '__main__':
    main()
