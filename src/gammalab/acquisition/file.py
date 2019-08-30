from ..service import ThreadService, SourceService
from ..wire import RawWire

import time
import numpy

pyaudio_nbytes=dict(float32=4)

class RawReplay(ThreadService, SourceService):
    def __init__(self, filename="data.raw", frames_per_buffer=1024, realtime=True):
        SourceService.__init__(self)
        ThreadService.__init__(self)
        self.CHANNELS=1
        self.RATE=48000
        self.FORMAT="float32"
        self.filename=filename
        self.frames_per_buffer=frames_per_buffer
        self.realtime=realtime

    def output_protocol(self, wire):
        assert isinstance(wire, RawWire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
    
    def process(self, data=None):
        if self.realtime:
          time.sleep(self.frames_per_buffer/(1.*self.RATE))
          t=time.time()
          dt=t-self.t0
          self.t0=t
          n=int(dt*self.RATE/16)*16
        else:
          n=int(self.frames_per_buffer/16)*16
        data=self._file.read(pyaudio_nbytes[self.FORMAT]*n)
        if len(data)==0:
          data=None
          self.done=True
        return data
        
    def start(self):
        self.t0=time.time()
        self._file=open(self.filename, "rb")
        ThreadService.start(self)

    def close(self):
        ThreadService.close(self)
        self._file.close()

