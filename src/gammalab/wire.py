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


# Wires are Queues. 
# Different queues are defined for checking purposes.
# data format of the wires is implcit but:
# wires may carry attributes as means to transfer meta information
# and this should be only comm between services! 
# maybe:
# message over wire: data+protocol or protocol as attribute for wire?
