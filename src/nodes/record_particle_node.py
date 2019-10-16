import os

import h5py

from src.com import Message, Node

directory = '../../data/'
file_name = 'SN12_test.hdf5'

node = Node('recorder')
kill = node.kill_flag()
sub_high_gain = node.Subscriber('mfli/high_gain')
sub_low_gain = node.Subscriber('mfli/low_gain')
sub_drive_voltage = node.Subscriber('mfli/peak_voltage')
sub_freq = node.Subscriber('mfli/freq')
node.register_node()

recv = []
while len(recv) == 0:
    recv = sub_high_gain.read()
close = Message(recv[-1]).data[-1]

recv = []
while len(recv) == 0:
    recv = sub_low_gain.read()
wide = Message(recv[-1]).data[-1]

recv = []
while len(recv) == 0:
    recv = sub_drive_voltage.read()
drive_voltage = Message(recv[-1]).data

recv = []
while len(recv) == 0:
    recv = sub_freq.read()
frequency = Message(recv[-1]).data

assert not os.path.isfile(directory + file_name)

with h5py.File(directory + file_name, 'a') as f:
    f.create_dataset('close', data=[close], compression='gzip', maxshape=(None, 2))
    f.create_dataset('wide', data=[wide], compression='gzip', maxshape=(None, 2))
    f.create_dataset('drive_voltage', data=drive_voltage)
    f.create_dataset('frequency', data=frequency)

print('recording')
while not kill:
    recv = []
    while len(recv) == 0:
        recv = sub_high_gain.read()
    close = Message(recv[-1]).data

    recv = []
    while len(recv) == 0:
        recv = sub_low_gain.read()
    wide = Message(recv[-1]).data

    with h5py.File(directory + file_name, 'a') as f:
        f['close'].resize(len(f['close']) + len(close), 0)
        f['close'][-len(close):] = close

        f['wide'].resize(len(f['wide']) + len(wide), 0)
        f['wide'][-len(wide):] = wide
