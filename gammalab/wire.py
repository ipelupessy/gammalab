try:
    from queue import Queue
except:
    from Queue import Queue

class RawWire(Queue):
    _description="Raw byte (string)"

class FloatWire(Queue):
    _description="numpy float array"

# Wires are Queues. 
# Different queues are defined for checking purposes.
# It is up to the implementation to conform to description.
