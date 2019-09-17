from mfli_message import MFLIMessage
from motor_message import MotorMessage

SERVER_IP = '192.168.0.108'
PUBLISHER_PORT = '5559'
SUBSCRIBER_PORT = '5558'
PUB_ADDR = "tcp://%s:%s" % (SERVER_IP, PUBLISHER_PORT)
SUB_ADDR = "tcp://%s:%s" % (SERVER_IP, SUBSCRIBER_PORT)
