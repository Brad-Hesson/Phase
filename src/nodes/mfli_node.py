import numpy as np

from src.com import Message, Node
from src.mfli import apply_settings, create_api_ref

pkv = 7.0
window = 2000
filter_freq = 100
filter_order = 8


def main():
    daq = create_api_ref()
    apply_settings(pkv, filter_freq, filter_order)
    daq.subscribe('/dev3934/demods/0/sample')
    daq.subscribe('/dev3934/demods/1/sample')
    clock_base = daq.getDouble('/dev3934/clockbase')

    close = np.zeros((0, 2), dtype=np.complex)
    wide = np.zeros((0, 2), dtype=np.complex)

    node = Node('mfli')
    kill = node.kill_flag()
    pub_high_gain = node.Publisher('mfli/high_gain')
    pub_low_gain = node.Publisher('mfli/low_gain')
    pub_drive_voltage = node.Publisher('mfli/peak_voltage')
    pub_filter_cutoff = node.Publisher('mfli/filter_cutoff')
    pub_filter_order = node.Publisher('mfli/filter_order')
    sub_calibration = node.Subscriber('mfli/calibration')
    node.register_node()

    msg = Message()
    calib = np.complex(1, 0)

    print('Sending Data')
    while not kill:
        data = daq.poll(0.1, 500, 7)['dev3934']['demods']
        packet = sub_calibration.read()
        calib = Message(packet[-1]).data if len(packet) > 0 else calib
        for channel in data:
            t = [complex(t / clock_base, 0) for t in data[channel]['sample']['timestamp']]
            c = [complex(x, y) * 2 ** 1.5 * calib for x, y in zip(data[channel]['sample']['x'], data[channel]['sample']['y'])]
            close = np.array([t, c]).transpose() if channel == '0' else close
            wide = np.array([t, c]).transpose() if channel == '1' else wide

        msg.data = pkv
        pub_drive_voltage.publish(msg)
        msg.data = filter_freq
        pub_filter_cutoff.publish(msg)
        msg.data = filter_order
        pub_filter_order.publish(msg)
        msg.data = close
        pub_high_gain.publish(msg)
        msg.data = wide
        pub_low_gain.publish(msg)


if __name__ == '__main__':
    main()
