import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(inspect.getfile(inspect.currentframe())))
import clr
import time
import threading

clr.AddReference("System")
clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("ThorLabs.MotionControl.KCube.DCServoCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")

# noinspection PyUnresolvedReferences
from System.Collections.Generic import Dictionary
# noinspection PyUnresolvedReferences
from System import Decimal, UInt64, String, Object
# noinspection PyUnresolvedReferences
from System import Convert
# noinspection PyUnresolvedReferences
from System import Action
# noinspection PyUnresolvedReferences
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo as KCubeDCServoCLI
# noinspection PyUnresolvedReferences
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
# noinspection PyUnresolvedReferences
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceConfiguration
# noinspection PyUnresolvedReferences
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceSettings
# noinspection PyUnresolvedReferences
from Thorlabs.MotionControl.GenericMotorCLI import MotorDirection


def non_blocking(x):
    return None


class KCubeDCServo(object):
    def __init__(self, polling_rate=100):
        self.polling_rate = polling_rate
        self.ser_num = None
        self.device = None

    def connect(self, timeout=5):
        start = time.time()
        DeviceManagerCLI.Initialize()
        while True:
            if (time.time() - start) > timeout:
                raise RuntimeError("Timeout during device discovery.")
                return None
            DeviceManagerCLI.BuildDeviceList()
            if len(DeviceManagerCLI.GetDeviceList()):
                break
        ser_num = DeviceManagerCLI.GetDeviceList()[0]
        self.ser_num = ser_num
        while True:
            if (time.time() - start) > timeout:
                raise RuntimeError("Timeout during connection to device.")
                return None
            try:
                self.device = KCubeDCServoCLI.CreateKCubeDCServo(ser_num)
                self.device.Connect(ser_num)
            except Exception as e:
                continue
            break

        while True:
            if (time.time() - start) > timeout:
                raise RuntimeError("Timeout during device initilization.")
                return None
            try:
                init = self.device.IsSettingsInitialized()
            except BaseException as e:
                raise e
                return None
            if init:
                break
        self.device.StartPolling(self.polling_rate)
        time.sleep(0.5)
        self.device.EnableDevice()
        time.sleep(0.5)
        self.device.LoadMotorConfiguration(ser_num, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
        return self

    def get_info(self):
        return self.device.GetDeviceInfo()

    def disconnect(self):
        self.device.Disconnect()

    def home(self, cb=None):
        if not self.is_busy():
            f = cb is None
            if f:
                e = threading.Event()
                cb = lambda x: e.set()

            self.device.Home(Action[UInt64](cb))

            if f:
                e.wait()

    def move_to(self, position, cb=None):
        if not self.is_busy():
            f = cb is None
            if f:
                e = threading.Event()
                cb = lambda x: e.set()

            self.device.MoveTo(Decimal(position), Action[UInt64](cb))

            if f:
                e.wait()

    def move_relative(self, distance, cb=None):
        if not self.is_busy():
            f = cb is None
            if f:
                e = threading.Event()
                cb = lambda x: e.set()

            direction = MotorDirection.Forward if distance >= 0 else MotorDirection.Backward
            self.device.SetVelocityParams(Decimal(2.6), Decimal(4))
            self.device.MoveRelative(direction, Decimal(abs(distance)), Action[UInt64](cb))

            if f:
                e.wait()

    def set_velocity(self, velocity):
        self.device.SetVelocityParams(Decimal(max(0, min(2.6, abs(velocity)))), Decimal(4))

    def move_continuous(self, direction):
        if not (self.is_busy() or self.is_moving()):
            mdir = MotorDirection.Backward if direction < 0 else MotorDirection.Forward
            self.device.MoveContinuous(mdir)

    def is_busy(self):
        return bool(self.device.IsDeviceBusy)

    def is_moving(self):
        bits = self.device.GetStatusBits()
        return bool((bits & (0x10 | 0x20)) > 0)

    def is_homed(self):
        bits = self.device.GetStatusBits()
        return bool((bits & 0x400) > 0)

    def get_position(self):
        return float(Convert.ToDouble(self.device.DevicePosition))

    def move_velocity(self, velocity):
        self.set_velocity(velocity)
        self.move_continuous(velocity)

    def stop(self, cb=None):
        f = cb is None
        if f:
            e = threading.Event()
            cb = lambda x: e.set()
        self.device.Stop(Action[UInt64](cb))
        if f:
            e.wait()


if __name__ == '__main__':
    m = KCubeDCServo().connect()

    s = m.device.MotorDeviceSettings
    l = s.FullPropertyList()
    print([t.Title for t in l])
    print(l[1].UseType)



