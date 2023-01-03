import numpy
import time
from ..service import SourceService, ThreadService
from ..wire import FloatWire

class Noise(ThreadService, SourceService):
    output_wire_class=FloatWire
    def __init__(self, frames_per_buffer=2048):
        super().__init__()
        self.CHANNELS=1
        self.RATE=48000
        self.FORMAT="float32"
        self.t0=time.time()
        self.frames_per_buffer=frames_per_buffer

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
    
    def process(self, data=None):
        time.sleep(self.frames_per_buffer/(1.*self.RATE))
        t=time.time()
        dt=t-self.t0
        self.t0=t
        
        n=int(numpy.floor(dt*self.RATE))
        data=numpy.random.random(n).astype("float32")
        return dict(data=data)

