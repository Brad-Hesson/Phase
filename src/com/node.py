import json
import socket
import struct
import threading
import time

import zmq

ping_rate = 0.5
multicast_group = ('224.0.0.1', 5555)


class Node(object):
    def __init__(self, name):
        self.__name = name + ':' + str(time.time())
        self.__nodes = dict()
        self.__publishers = dict()
        self.__subscribers = set()
        self.__update_thread = threading.Thread(target=self.__update)
        self.__update_thread.setDaemon(True)
        self.__context = zmq.Context.instance()

        self.__init_socket()

    def register_node(self):
        self.__update_thread.start()

    def Publisher(self, topic):
        publisher = Publisher(topic, self)
        assert topic not in self.__publishers
        self.__publishers[topic] = publisher.port
        return publisher

    def Subscriber(self, topic):
        subscriber = Subscriber(topic, self)
        assert subscriber not in self.__subscribers
        self.__subscribers.add(subscriber)
        return subscriber

    def kill_flag(self):
        sub = self.Subscriber('kill')
        return NodeFlag(sub)

    def __init_socket(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', multicast_group[1]))
        group = socket.inet_aton(multicast_group[0])
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 2))
        self.__socket.settimeout(ping_rate)

    def __tick(self):
        msg = (self.name, self.__publishers)
        self.__socket.sendto(json.dumps(msg), multicast_group)

    def __parse_message(self, data, address):
        name, topics = json.loads(data)
        topics = {str(topic): (str(address[0]), port) for topic, port in topics.items()}
        self.__nodes[str(name)] = (time.time(), topics)

    def __update(self):
        run = True
        while run:
            while True:
                try:
                    data, address = self.__socket.recvfrom(1024)
                except socket.timeout:
                    break
                self.__parse_message(data, address)
            for name, data in self.__nodes.items():
                if time.time() - data[0] > ping_rate * 10:
                    del self.__nodes[name]
            self.__tick()
            for subscriber in self.__subscribers:
                subscriber.update()

    @property
    def name(self):
        return self.__name

    @property
    def nodes(self):
        nodes = set(self.__nodes.keys())
        nodes.add(self.name)
        return nodes

    @property
    def topics(self):
        topics = {topic: {('localhost', port)} for topic, port in self.__publishers.items()}
        for node in self.__nodes.values():
            for topic, address in node[1].items():
                topics[topic] = topics[topic].union({address, }) if topic in topics else {address, }
        return topics


class Publisher(object):
    def __init__(self, topic, node):
        self.__topic = topic
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

    def publish(self, data):
        self.__socket.send('%s %s' % (self.__topic, data))

    def close(self):
        self.__socket.close()

    @property
    def port(self):
        return self.__port

    @property
    def topic(self):
        return self.__topic

    def __hash__(self):
        return hash(self.topic)


class Subscriber(object):
    def __init__(self, topic, node):
        self.__topic = topic
        self.__node = node
        self.__sockets = dict()

    def update(self):
        addresses = self.__node.topics[self.topic] if self.topic in self.__node.topics else set()
        for address in addresses.union(self.__sockets):
            if address not in self.__sockets:
                sock = zmq.Context.instance().socket(zmq.SUB)
                sock.connect("tcp://%s:%s" % address)
                sock.setsockopt(zmq.SUBSCRIBE, self.topic)
                sock.setsockopt(zmq.RCVTIMEO, 0)
                self.__sockets[address] = sock
            if address not in addresses:
                self.__sockets[address].close()
                del self.__sockets[address]

    def read(self):
        data = list()
        for sock in self.__sockets.values():
            while True:
                try:
                    data.append(sock.recv().split(' ', 1)[1])
                except zmq.Again:
                    break
        return data

    @property
    def topic(self):
        return self.__topic

    def __hash__(self):
        return hash(self.topic)


class NodeFlag(object):
    def __init__(self, subscriber):
        self.__sub = subscriber

    def __nonzero__(self):
        return len(self.__sub.read()) > 0


if __name__ == '__main__':
    node = Node('test')
    node.register_node()
    kill = node.kill_flag()

    while not kill:
        print('running')
        time.sleep(0.5)
