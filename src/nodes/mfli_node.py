import numpy as np
import zmq

from src.com import MFLIMessage
from src.mfli import apply_settings, create_api_ref

pkv = 7.0
window = 2000
filter_freq = 100
filter_order = 8
port = 5556

daq = create_api_ref()
apply_settings(pkv, filter_freq, filter_order)
daq.subscribe('/dev3934/demods/0/sample')
daq.subscribe('/dev3934/demods/1/sample')
clock_base = daq.getDouble('/dev3934/clockbase')

close = np.zeros((0, 2), dtype=np.complex)
wide = np.zeros((0, 2), dtype=np.complex)

msg = MFLIMessage()
msg.drive_voltage = pkv
msg.filter_cutoff = filter_freq
msg.filter_order = filter_order
msg.clock_base = clock_base

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % str(port))

print('Sending Data')
RUN = True
while RUN:
    data = daq.poll(0.1, 500, 7)['dev3934']['demods']
    for channel in data:
        t = [complex(t, 0) for t in data[channel]['sample']['timestamp']]
        c = [complex(x, y) * 2 ** 1.5 for x, y in zip(data[channel]['sample']['x'], data[channel]['sample']['y'])]

        close = np.array([t, c]).transpose() if channel == '0' else close
        wide = np.array([t, c]).transpose() if channel == '1' else wide

    msg.data_high_gain = close
    msg.data_low_gain = wide

    socket.send("%s %s" % (str(port), msg.encode()))
