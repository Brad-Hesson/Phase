import os
import h5py
from src.com import Message, Node

directory = '../../data/'
file_name = 'SN12_temp_ramp_test.hdf5'


def main():
    node = Node('recorder')
    kill = node.kill_flag()
    recv_high_gain = node.Receiver('mfli/high_gain')
    recv_low_gain = node.Receiver('mfli/low_gain')
    recv_drive_voltage = node.Receiver('mfli/peak_voltage')
    recv_freq = node.Receiver('mfli/freq')
    recv_temp = node.Receiver('watlow/temp')
    recv_setpoint = node.Receiver('watlow/setpoint')
    node.register_node()

    recv = None
    while recv is None:
        recv = recv_high_gain.read()
    close = Message(recv).data[-1]

    recv = None
    while recv is None:
        recv = recv_low_gain.read()
    wide = Message(recv).data[-1]

    recv = None
    while recv is None:
        recv = recv_drive_voltage.read()
    drive_voltage = Message(recv).data

    recv = None
    while recv is None:
        recv = recv_freq.read()
    frequency = Message(recv).data

    recv = None
    while recv is None:
        recv = recv_temp.read()
    temp = Message(recv).data

    recv = None
    while recv is None:
        recv = recv_setpoint.read()
    setpoint = Message(recv).data

    assert not os.path.isfile(directory + file_name)
    f = h5py.File(directory + file_name, 'a')

    f.create_dataset('close', data=[close], compression='gzip', maxshape=(None, 2))
    f.create_dataset('wide', data=[wide], compression='gzip', maxshape=(None, 2))
    f.create_dataset('temp', data=[temp], compression='gzip', maxshape=(None, 2))
    f.create_dataset('setpoint', data=[setpoint], compression='gzip', maxshape=(None, 2))
    f.create_dataset('drive_voltage', data=drive_voltage)
    f.create_dataset('frequency', data=frequency)

    print('recording')
    while not kill:
        recv = recv_high_gain.read()
        if recv is not None:
            f['close'].resize(len(f['close']) + 1, 0)
            f['close'][-1] = Message(recv).data[-1]

        recv = recv_low_gain.read()
        if recv is not None:
            f['wide'].resize(len(f['wide']) + 1, 0)
            f['wide'][-1] = Message(recv).data[-1]

        recv = recv_temp.read()
        if recv is not None:
            f['temp'].resize(len(f['temp']) + 1, 0)
            f['temp'][-1] = Message(recv).data

        recv = recv_setpoint.read()
        if recv is not None:
            f['setpoint'].resize(len(f['setpoint']) + 1, 0)
            f['setpoint'][-1] = Message(recv).data


if __name__ == '__main__':
    main()
