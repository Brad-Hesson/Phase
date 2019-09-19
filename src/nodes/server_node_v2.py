import socket
import struct

message = 'test'
multicast_group = ('224.3.29.71', 10000)

def main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    try:
        print('sending "%s"' % message)
        sock.sendto(message, multicast_group)

        try:
            print('waiting for response')
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print('timed out')
            start_server()
        else:
            print('received "%s" from %s' % (data, server))

    finally:
        print('closing socket')
        sock.close()


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', multicast_group[1]))
    group = socket.inet_aton(multicast_group[0])
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(1024)

        print('received %s bytes from %s' % (len(data), address))
        print(data)

        print('sending acknowledgement to', address)
        sock.sendto('ack', address)


if __name__ == '__main__':
    main()
