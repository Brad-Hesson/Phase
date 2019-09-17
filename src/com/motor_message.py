from msg import Message


class MotorMessage(Message):
    def __init__(self, serialized=None):
        self.motor_position = float()
        Message.__init__(self, serialized)
