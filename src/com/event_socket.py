import struct
import socket
import threading
import json
import zlib


ping_rate = 0.5
multicast_group = ('224.0.0.1', 60000)
index = 1


def main():
    sock = EventSocket(socket.SOCK_DGRAM, printer)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', multicast_group[1]))
    group = socket.inet_aton(multicast_group[0])
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    raw_input()

    sock.close()


def printer((msg, address)):
    global index
    print('[%d] %s (%s)' % (index, str(Message(msg).name), address[0]))
    index += 1


class EventSocket(object):
    def __init__(self, socket_type, cb=None, **kwargs):
        self.__socket = socket.socket(socket.AF_INET, socket_type)
        self.__socket.settimeout(0.1)
        self.cb = cb
        self.__run = None

    def bind(self, *args, **kwargs):
        self.__socket.bind(*args, **kwargs)
        self.__run = True
        thread = threading.Thread(target=self.__loop)
        thread.setDaemon(True)
        thread.start()

    def connect(self, *args, **kwargs):
        val = self.__socket.connect(*args, **kwargs)
        self.__run = True
        thread = threading.Thread(target=self.__loop)
        thread.setDaemon(True)
        thread.start()
        return val

    def sendto(self, *args, **kwargs):
        return self.__socket.sendto(*args, **kwargs)

    def setsockopt(self, *args, **kwargs):
        return self.__socket.setsockopt(*args, **kwargs)

    def getsockopt(self, *args, **kwargs):
        return self.__socket.getsockopt(*args, **kwargs)

    def close(self):
        self.__run = False
        while self.__run is not None:
            pass

    def __loop(self):
        while self.__run and self.cb is not None:
            try:
                msg = self.__socket.recvfrom(1024)
                thread = threading.Thread(target=self.cb, args=(msg,))
                thread.setDaemon(True)
                thread.start()
            except socket.timeout:
                pass
        self.__socket.close()
        self.__run = None


class Message(object):
    compress = True

    def __init__(self, serialized=None):
        self.decode(serialized) if serialized is not None else None

    def encode(self):
        d = json.dumps(self.__dict__)
        return zlib.compress(d, 1) if self.compress else d

    def decode(self, serialized):
        d = json.loads(zlib.decompress(serialized) if self.compress else serialized)
        for attr in d:
            self.__dict__[attr] = d[attr]

    def __repr__(self):
        return self.encode()


if __name__ == '__main__':
    main()
