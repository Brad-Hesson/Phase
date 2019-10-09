import time

import minimalmodbus
import numpy as np
import serial

from src.com import Node, Message


def main():
    node = Node('watlow')
    tran_temp = node.Transmitter('watlow/temp')
    tran_power = node.Transmitter('watlow/power')
    tran_setpoint = node.Transmitter('watlow/setpoint')
    recv_set_setpoint = node.Receiver('watlow/set_setpoint')
    kill_flag = node.kill_flag()
    node.register_node()
    msg = Message()

    minimalmodbus.close_port_after_each_call = True
    instrument = minimalmodbus.Instrument('COM6', 1)  # port name, slave address (in decimal)
    instrument.serial.baudrate = 9600   # Baud
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 0.5   # seconds
    instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode

    print('running')
    while not kill_flag:
        recv = recv_set_setpoint.read()
        if recv is not None:
            instrument.write_float(2640, Message(recv).data)
        temp = instrument.read_float(402)
        power = instrument.read_float(2384)
        set_point = instrument.read_float(2652)
        millis = time.time()

        msg.data = np.array((millis, temp))
        tran_temp.transmit(msg)
        msg.data = np.array((millis, power))
        tran_power.transmit(msg)
        msg.data = np.array((millis, set_point))
        tran_setpoint.transmit(msg)


if __name__ == '__main__':
    main()
