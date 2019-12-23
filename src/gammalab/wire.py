try:
    from queue import Queue
except:
    from Queue import Queue

class Wire(Queue):
    __initialized=False
    _description="none"

    def __init__(self, **kwargs):
        Queue.__init__(self, **kwargs)
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

class FloatWire(Queue):
    _description="numpy float array"

class PulseWire(Queue):
    _description="pulses"

class MessageWire(Queue):
    _description="output queue for terminal messages"

class HistogramWire(Queue):
    _description="dict with histogram"

