import numpy as np
from zhinst.utils import bw2tc
from zhinst.ziPython import ziDiscovery, ziDAQServer


# noinspection PyArgumentList
def create_api_ref():
    discovery = ziDiscovery()
    device = discovery.findAll()[0]
    device_properties = discovery.get(device)
    ip = device_properties['serveraddress']
    port = device_properties['serverport']
    api_level = device_properties['apilevel']
    daq = ziDAQServer(ip, port, api_level)
    daq.connect()
    return daq


def set_pkpk(daq, pkv):
    # settings required for test
    daq.subscribe('/dev3934/scopes/0/wave')
    daq.setInt('/dev3934/scopes/0/time', 0)
    daq.setDouble('/dev3934/scopes/0/length', 16384)
    daq.setDouble('/dev3934/scopes/0/triglevel', 0)
    daq.setInt('/dev3934/scopes/0/channels/0/inputselect', 8)
    daq.setInt('/dev3934/scopes/0/trigchannel', 8)
    daq.setInt('/dev3934/scopes/0/trigenable', 1)
    daq.setInt('/dev3934/scopes/0/enable', 0)
    daq.setInt('/dev3934/scopes/0/enable', 1)

    # get the output voltage setting
    output = daq.getDouble('/dev3934/sigouts/0/amplitudes/1')

    # test the actual output voltage
    data = {}
    daq.flush()
    while '/dev3934/scopes/0/wave' not in data:
        data = daq.poll(0.1, 10, 7, True)
    wave = data['/dev3934/scopes/0/wave'][-1]['wave']*data['/dev3934/scopes/0/wave'][-1]['channelscaling'][0]
    actual = np.std(wave)*2**1.5

    # using the calculated factor, set the actual voltage
    daq.setDouble('/dev3934/sigouts/0/amplitudes/1', pkv * output / actual)

    # test the actual output voltage
    data = {}
    daq.flush()
    while '/dev3934/scopes/0/wave' not in data:
        data = daq.poll(0.1, 10, 7, True)
    wave = data['/dev3934/scopes/0/wave'][-1]['wave'] * data['/dev3934/scopes/0/wave'][-1]['channelscaling'][0]
    daq.unsubscribe('/dev3934/scopes/0/wave')
    daq.flush()
    daq.flush()
    return np.std(wave)*2**1.5, output / actual


def apply_settings(pkv=7, freq=100000, filter_freq=1000, filter_order=8):
    daq = create_api_ref()
    # Signal Input 1
    daq.setInt('/dev3934/demods/0/adcselect', 0)
    daq.setInt('/dev3934/sigins/0/float', 0)
    daq.setInt('/dev3934/sigins/0/diff', 0)
    daq.setInt('/dev3934/sigins/0/imp50', 0)
    daq.setInt('/dev3934/sigins/0/ac', 1)
    daq.setDouble('/dev3934/sigins/0/range', 3)
    daq.setDouble('/dev3934/sigins/0/scaling', 1)

    # Filter 1
    daq.setInt('/dev3934/demods/0/order', filter_order)
    daq.setDouble('/dev3934/demods/0/timeconstant', bw2tc(filter_freq, 8))
    daq.setInt('/dev3934/demods/0/sinc', 0)

    # Data Transfer 1
    daq.setDouble('/dev3934/demods/0/rate', 1674)
    daq.setInt('/dev3934/demods/0/enable', 1)

    # Signal Input 2
    daq.setInt('/dev3934/demods/1/adcselect', 9)

    # Filter 2
    daq.setInt('/dev3934/demods/1/order', filter_order)
    daq.setDouble('/dev3934/demods/1/timeconstant', bw2tc(filter_freq, 8))
    daq.setInt('/dev3934/demods/1/sinc', 0)

    # Data Transfer 2
    daq.setDouble('/dev3934/demods/1/rate', 1674)
    daq.setInt('/dev3934/demods/1/enable', 1)

    # Reference
    daq.setDouble('/dev3934/oscs/0/freq', freq)
    daq.setDouble('/dev3934/demods/1/harmonic', 1)
    daq.setDouble('/dev3934/demods/1/phaseshift', 0)

    # Output
    daq.setInt('/dev3934/sigouts/0/enables/1', 1)
    daq.setDouble('/dev3934/sigouts/0/offset', 0)
    daq.setDouble('/dev3934/sigouts/0/range', 10)
    daq.setInt('/dev3934/sigouts/0/add', 0)
    daq.setInt('/dev3934/sigouts/0/diff', 0)
    daq.setInt('/dev3934/sigouts/0/on', 1)
    daq.setInt('/dev3934/sigouts/0/imp50', 0)
    output, _ = set_pkpk(daq, pkv)
    assert abs(pkv - output) / pkv < 0.05


if __name__ == '__main__':
    dack = create_api_ref()
    RUN = False
    node = '/dev3934'
    while RUN:
        leafs = dack.listNodes(node, 4)
        nodes = [n for n in dack.listNodes(node, 0) if n not in leafs]
        opts = nodes+leafs
        print('---------- ' + node + ' ----------')
        i = 1
        for opt in opts:
            n = opt if i <= len(nodes) else opt.lower()
            print('%2.f: /%s' % (i, n))
            i += 1

        ipt = input()
        if ipt == 'q':
            RUN = False
        elif ipt in ('..', 0):
            new = node.rpartition('/')[0]
            node = node if new == '' else new
        else:
            node = node + '/' + opts[ipt-1]

    print(set_pkpk(dack, 4.5))
