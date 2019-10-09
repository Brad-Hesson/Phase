import socket
import struct
import threading
import time
from collections import defaultdict

import zmq

from src.com import Message

tick_rate = 0.1
multicast_group = ('224.0.0.1', 5555)


class Node(object):
    def __init__(self, name):
        self.__name = name + ':' + str(time.time())
        self.__nodes = dict()
        self.__channels = dict()
        self.__topics = dict()
        self.transmitters = set()
        self.receivers = set()
        self.publishers = set()
        self.subscribers = set()
        self.__run = False
        self.__socket = None

    def register(self):
        self.__init_socket()
        self.__run = True
        thread = threading.Thread(target=self.__loop)
        thread.setDaemon(True)
        thread.start()

    def close(self):
        self.__run = False
        for tran in self.transmitters.copy():
            tran.close()
        for recv in self.receivers.copy():
            recv.close()
        while self.__run is not None:
            pass
        self.__nodes = dict()

    def Transmitter(self, channel):
        transmitter = Transmitter(channel, self)
        assert transmitter not in self.transmitters
        self.transmitters.add(transmitter)
        return transmitter

    def Receiver(self, channel, cb=None):
        receiver = Receiver(channel, self, cb)
        assert receiver not in self.receivers
        self.receivers.add(receiver)
        return receiver

    def kill_flag(self):
        recv = self.Receiver('kill')
        return NodeFlag(recv)

    def __init_socket(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', multicast_group[1]))
        group = socket.inet_aton(multicast_group[0])
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 2))
        self.__socket.settimeout(tick_rate)

    def __tick(self):
        msg = Message()
        msg.channels = {transmitter.channel: transmitter.port for transmitter in self.transmitters}
        msg.topics = {publisher.topic: publisher.port for publisher in self.publishers}
        msg.name = self.name
        self.__socket.sendto(msg.encode(), multicast_group)

    def __parse_message(self, data, address, now):
        msg = Message(data)
        self.__nodes[str(msg.name)] = now
        self.__delete_links(msg.name)
        for channel, port in msg.channels.iteritems():
            self.__channels[(str(msg.name), str(channel))] = (address[0], port)
        for topic, port in msg.topics.iteritems():
            self.__topics[(str(msg.name), str(topic))] = (address[0], port)

    def __delete_links(self, name):
        for key in self.__channels.keys():
            if key[0] == name:
                del self.__channels[key]
        for key in self.__topics.keys():
            if key[0] == name:
                del self.__topics[key]

    def __loop(self):
        while self.__run:
            now = time.time()

            self.__tick()

            while True:
                try:
                    data, address = self.__socket.recvfrom(1024)
                except socket.timeout:
                    break
                self.__parse_message(data, address, now)

            for name, timestamp in self.__nodes.items():
                if now - timestamp > tick_rate * 10:
                    self.__delete_links(name)
                    del self.__nodes[name]

            for receiver in self.receivers:
                receiver.update()

        self.__socket.close()
        self.__run = None

    @property
    def name(self):
        return self.__name

    @property
    def nodes(self):
        nodes = set(self.__nodes.keys())
        return nodes

    @property
    def channels(self):
        channels = defaultdict(set)
        for key, value in self.__channels.iteritems():
            channels[key[1]].add(value)
        return dict(channels)

    @property
    def topics(self):
        topics = defaultdict(set)
        for key, value in self.__topics.iteritems():
            topics[key[1]].add(value)
        return dict(topics)


class Transmitter(object):
    def __init__(self, channel, node):
        self.__channel = channel
        self.__node = node
        self.__socket = zmq.Context.instance().socket(zmq.PUB)
        self.__port = 5550

        while True:
            try:
                self.__socket.bind("tcp://%s:%s" % ('*', self.__port))
            except zmq.ZMQError:
                self.__port += 1
                continue
            break

    def transmit(self, data):
        self.__socket.send('%s %s' % (self.__channel, data))

    def close(self):
        self.__socket.close()
        self.__node.transmitters.remove(self)

    @property
    def port(self):
        return self.__port

    @property
    def channel(self):
        return self.__channel

    def __hash__(self):
        return hash(self.channel)


class Receiver(object):
    def __init__(self, channel, node, cb=None):
        self.__channel = channel
        self.__node = node
        self.__sockets = dict()
        self.__buffer = list()
        self.__buffer_lock = threading.Lock()
        self.__buffer_max = 64
        self.__cb = cb

    def update(self):
        addresses = self.__node.channels[self.channel] if self.channel in self.__node.channels else set()
        for address in addresses.union(self.__sockets):
            if address not in self.__sockets:
                sock = EventSocket(zmq.SUB, self.__recv_cb)
                sock.setsockopt(zmq.SUBSCRIBE, self.channel)
                sock.connect("tcp://%s:%s" % address)
                self.__sockets[address] = sock
            if address not in addresses:
                self.__sockets[address].close()
                del self.__sockets[address]

    def __recv_cb(self, msg):
        if self.__cb is None:
            if len(self.__buffer) <= self.__buffer_max:
                with self.__buffer_lock:
                    self.__buffer.append(msg.split(' ', 1)[1])
            else:
                raise UserWarning('Receive buffer overflow for channel: '+str(self.channel))
        else:
            self.__cb(msg.split(' ', 1)[1])

    def read(self):
        assert self.__cb is None
        with self.__buffer_lock:
            if len(self.__buffer) > 0:
                return self.__buffer.pop(0)
            else:
                return None

    def close(self):
        for key, sock in self.__sockets.items():
            sock.close()
            del self.__sockets[key]
        self.__node.receivers.remove(self)

    @property
    def channel(self):
        return self.__channel

    def __hash__(self):
        return hash(self.channel)


class NodeFlag(object):
    def __init__(self, receiver):
        self.__recv = receiver

    def __nonzero__(self):
        return self.__recv.read() is not None


class EventSocket(object):
    def __init__(self, socket_type, cb=None, **kwargs):
        self.__socket = zmq.Context.instance().socket(socket_type, **kwargs)
        self.__socket.setsockopt(zmq.RCVTIMEO, 100)
        self.cb = cb
        self.__run = None

    def bind(self, *args, **kwargs):
        val = self.__socket.bind(*args, **kwargs)
        self.__run = True
        thread = threading.Thread(target=self.__loop)
        thread.setDaemon(True)
        thread.start()
        return val

    def connect(self, *args, **kwargs):
        val = self.__socket.connect(*args, **kwargs)
        self.__run = True
        thread = threading.Thread(target=self.__loop)
        thread.setDaemon(True)
        thread.start()
        return val

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
                msg = self.__socket.recv()
                thread = threading.Thread(target=self.cb, args=(msg,))
                thread.setDaemon(True)
                thread.start()
            except zmq.Again:
                pass
        self.__socket.close()
        self.__run = None


if __name__ == '__main__':
    node = Node('iPython_Console')
    node.register()


