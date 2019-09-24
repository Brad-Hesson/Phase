import json
import zlib

import numpy as np

compress = True


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.ndarray):
            return {'__type__': 'ndarray', 'data': json.dumps(o.tolist(), cls=CustomEncoder)}
        if isinstance(o, complex):
            return {'__type__': 'complex', 'real': o.real, 'imag': o.imag}
        return json.JSONEncoder.default(self, o)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kargs)

    @staticmethod
    def object_hook(o):
        if '__type__' not in o:
            return o
        if o['__type__'] == 'ndarray':
            return np.array(json.loads(o['data'], cls=CustomDecoder))
        if o['__type__'] == 'complex':
            return complex(o['real'], o['imag'])


class Message(object):
    def __init__(self, serialized=None):
        self.data = -1
        self.decode(serialized) if serialized is not None else None

    def encode(self):
        d = json.dumps(self.__dict__, cls=CustomEncoder)
        return zlib.compress(d, 1) if compress else d

    def decode(self, serialized):
        d = json.loads(zlib.decompress(serialized) if compress else serialized, cls=CustomDecoder)
        for attr in self.__dict__:
            self.__setattr__(attr, d[attr]) if attr in d else None

    def __str__(self):
        return self.encode()

    def __repr__(self):
        return self.encode()
