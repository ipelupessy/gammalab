try:
    from queue import Queue
except:
    from Queue import Queue

class Wire(object):
    __initialized=False
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
        self.__initialized=True

# attributes are forwarded to the protocol (after __init__)
    def __setattr__(self, name, value):
        if self.__initialized:
            self.protocol[name] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name in self.protocol:
            return self.protocol[name]
        else:
            raise AttributeError("No such attribute in protocol: " + name)

    def __delattr__(self, name):
        if name in self.protocol:
            del self.protocol[name]
        else:
            raise AttributeError("No such attribute in protocol: " + name)

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

