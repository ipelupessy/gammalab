
from multiprocessing import Queue as Queue

class Wire(object):
    _initialized=False
    _description="none"

    def __init__(self, **kwargs):
        self._queue=Queue(**kwargs)

# forward the necessary methods; note we are not deriving class from Queue since 
# multiprocessing Queue import is a factory method
        self.get=self._queue.get
        self.put=self._queue.put
        self.put_nowait=self._queue.put_nowait
        self.get_nowait=self._queue.get_nowait
        
        self.protocol=dict()
        self._initialized=True

    def __getstate__(self):
        d=self.__dict__.copy()
        d["_initialized"]=False
        return self.__dict__

    def __setstate__(self, d):
        for x in d:
          setattr(self, x, d[x])
        self._initialized=True

# attributes are forwarded to the protocol (after __init__)
    def __setattr__(self, name, value):
        if self._initialized:
            self.protocol[name] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name in self.protocol:
            return self.protocol[name]
        else:
            raise AttributeError(f"No attribute {name} in protocol of {self.__class__.__name__} ")

    def __delattr__(self, name):
        if name in self.protocol:
            del self.protocol[name]
        else:
            raise AttributeError(f"No attribute {name} in protocol of {self.__class__.__name__} ")

class RawWire(Wire):
    _description="Raw byte (string)"

class FloatWire(Wire):
    _description="numpy float array"

class PulseWire(Wire):
    _description="pulses"

class MessageWire(Wire):
    _description="output queue for terminal messages"

class HistogramWire(Wire):
    _description="dict with histogram"

