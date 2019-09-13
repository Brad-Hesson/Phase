import os
import time

import h5py
import zmq

from src.com import MFLIMessage, SUB_ADDR

file_name = 'data' + '_%.0f.hdf5' % time.time()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(SUB_ADDR)
socket.setsockopt(zmq.SUBSCRIBE, 'mfli_node')
msg_first = MFLIMessage(socket.recv().split(' ', 1)[1])

high_gain_start = msg_first.data_high_gain[0, 0].real
low_gain_start = msg_first.data_low_gain[0, 0].real

close = msg_first.data_high_gain
wide = msg_first.data_low_gain

if not os.path.isfile(file_name):
    with h5py.File(file_name, 'a') as f:
        f.create_dataset('close', data=close, compression='gzip', maxshape=(None, 2))
        f.create_dataset('wide', data=wide, compression='gzip', maxshape=(None, 2))
        f.create_dataset('clock_base', data=msg_first.clock_base)
        f.create_dataset('filter_cutoff', data=msg_first.filter_cutoff)
        f.create_dataset('drive_voltage', data=msg_first.drive_voltage)

while True:
    with h5py.File(file_name, 'a') as f:
        f['close'].resize(len(f['close']) + len(close), 0)
        f['close'][-len(close):] = close

        f['wide'].resize(len(f['wide']) + len(wide), 0)
        f['wide'][-len(wide):] = wide

    msg = MFLIMessage(socket.recv().split(' ', 1)[1])

    close = msg.data_high_gain
    wide = msg.data_low_gain
