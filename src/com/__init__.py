from mfli_message import MFLIMessage

SERVER_IP = '192.168.0.170'
PUBLISHER_PORT = '5559'
SUBSCRIBER_PORT = '5558'
PUB_ADDR = "tcp://%s:%s" % (SERVER_IP, PUBLISHER_PORT)
SUB_ADDR = "tcp://%s:%s" % (SERVER_IP, SUBSCRIBER_PORT)
