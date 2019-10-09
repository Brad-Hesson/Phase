import numpy as np
from src.com import Message, Node
from src.mfli import apply_settings, create_api_ref

drive_voltage = 7.0
freq = 284000
window = 2000
filter_freq = 100
filter_order = 8

calibration = np.complex(1, 0)

def main():
    daq = create_api_ref()
    apply_settings(drive_voltage, freq, filter_freq, filter_order)
    daq.subscribe('/dev3934/demods/0/sample')
    daq.subscribe('/dev3934/demods/1/sample')
    clock_base = daq.getDouble('/dev3934/clockbase')

    close = np.zeros((0, 2), dtype=np.complex)
    wide = np.zeros((0, 2), dtype=np.complex)

    node = Node('mfli')
    kill = node.kill_flag()
    tran_high_gain = node.Transmitter('mfli/high_gain')
    tran_low_gain = node.Transmitter('mfli/low_gain')
    tran_drive_voltage = node.Transmitter('mfli/peak_voltage')
    tran_freq = node.Transmitter('mfli/freq')
    tran_filter_cutoff = node.Transmitter('mfli/filter_cutoff')
    tran_filter_order = node.Transmitter('mfli/filter_order')
    node.Receiver('mfli/calibration', calibration_cb)
    node.register()

    msg = Message()

    print('Sending Data')
    while not kill:
        data = daq.poll(0.1, 500, 7)['dev3934']['demods']
        for channel in data:
            t = [complex(t / clock_base, 0) for t in data[channel]['sample']['timestamp']]
            c = [complex(x, y) * 2 ** 1.5 * calibration for x, y in zip(data[channel]['sample']['x'], data[channel]['sample']['y'])]
            close = np.array([t, c]).transpose() if channel == '0' else close
            wide = np.array([t, c]).transpose() if channel == '1' else wide

        msg.data = drive_voltage
        tran_drive_voltage.transmit(msg)
        msg.data = freq
        tran_freq.transmit(msg)
        msg.data = filter_freq
        tran_filter_cutoff.transmit(msg)
        msg.data = filter_order
        tran_filter_order.transmit(msg)
        msg.data = close
        tran_high_gain.transmit(msg)
        msg.data = wide
        tran_low_gain.transmit(msg)


def calibration_cb(msg):
    global calibration
    calibration = Message(msg).data


if __name__ == '__main__':
    main()
