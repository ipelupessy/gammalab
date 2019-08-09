try:
    from queue import Queue
except:
    from Queue import Queue

class RawWire(Queue):
    _description="Raw byte (string)"

class FloatWire(Queue):
    _description="numpy float array"

class PulseWire(Queue):
    _description="pulses"

class MessageWire(Queue):
    _description="output queue for terminal messages"

class HistogramWire(Queue):
    _description="dict with histogram"

