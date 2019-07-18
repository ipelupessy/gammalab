import numpy
import time
from ..service import SourceService, ThreadService
from ..wire import RawWire

class Noise(ThreadService, SourceService):
    def __init__(self):
        SourceService.__init__(self)
        ThreadService.__init__(self)
        self.CHANNELS=1
        self.RATE=48000
        self.FORMAT="float32"
        self.t0=time.time()

    def output_protocol(self, wire):
        assert isinstance(wire, RawWire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
    
    def _samples(self):
        t=time.time()
        dt=t-self.t0
        self.t0=t
        
        n=int(numpy.floor(dt*self.RATE))
        data=numpy.random.random(n)
        return data.tobytes()
        
    def _process(self):
        while not self.done:
            if not self.stopped:
                data=self._samples()
                self.send_output(data)
            time.sleep(0.1)
