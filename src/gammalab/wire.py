try:
    from queue import Queue
except:
    from Queue import Queue

class Wire(Queue):
    _description="none"

    def __init__(self, **kwargs):
        super(Wire, self).__init__(**kwargs)
        self.protocol=Dict()

# attributes are forwarded to the protocol
    def __getattr__(self, name):
        try:
            return getattr(super(Wire, self), name)
        except AttributeError:
            if name in self.protocol:
                return self.protocol[name]
            else:
                raise AttributeError("No such attribute in protocol: " + name)

    def __setattr__(self, name, value):
        self.protocol[name] = value

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

