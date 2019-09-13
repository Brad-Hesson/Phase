import numpy as np

from msg import Message


class MFLIMessage(Message):
    def __init__(self, serialized=None):
        self.data_high_gain = np.array((0, 2), dtype=np.complex)
        self.data_low_gain = np.array((0, 2), dtype=np.complex)
        self.gain = np.array((0, 2), dtype=np.complex)
        self.clock_base = None
        self.filter_cutoff = None
        self.filter_order = None
        self.drive_voltage = None
        Message.__init__(self, serialized)
