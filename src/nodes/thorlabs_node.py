import zmq

from src.com import MotorMessage, PUB_ADDR
from src.thorlabs import KCubeDCServo


def main():
    motor = KCubeDCServo(polling_rate=100)
    motor.connect()
    print('Motor Connected')

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(PUB_ADDR)

    msg = MotorMessage()

    run = True
    while run:
        msg.motor_position = motor.get_position()

        socket.send("%s %s" % ('motor_node', msg.encode()))


if __name__ == '__main__':
    main()
