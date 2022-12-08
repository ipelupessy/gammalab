from ..service import ThreadService, SourceService
from ..wire import RawWire

import time
import numpy
import wave

pyaudio_nbytes=dict(int16=2, float32=4)

class RawReplay(ThreadService, SourceService):
    output_wire_class=RawWire
    def __init__(self, filename="data.raw", frames_per_buffer=1024, realtime=True, 
        sample_rate=48000, sample_format="float32"):
        super(RawReplay, self).__init__()
        self.CHANNELS=1
        self.RATE=sample_rate
        self.FORMAT=sample_format
        self.filename=filename
        self.frames_per_buffer=frames_per_buffer
        self.realtime=realtime

    def output_protocol(self, wire):
        super(RawReplay, self).output_protocol(wire)      
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
    
    def readframes(self,n):
        return self._file.read(pyaudio_nbytes[self.FORMAT]*n)
    
    def process(self, data=None):
        if self.realtime:
          time.sleep(self.frames_per_buffer/(1.*self.RATE))
          t=time.time()
          dt=t-self.t0
          self.t0=t
          n=int(dt*self.RATE/16)*16
        else:
          n=int(self.frames_per_buffer/16)*16
        data=self.readframes(n)
        if len(data)==0:
          data=None
          self.stopped=True
        return data
        
    def start_process(self):
        self.t0=time.time()
        self._file=open(self.filename, "rb")
        super(RawReplay, self).start_process()
        

    def cleanup(self):
        self._file.close()
        super(RawReplay, self).cleanup()


format_from_width={2 : "int16", 4 : "float32"}

class WavReplay(RawReplay):
    def __init__(self, filename, frames_per_buffer=1024, realtime=True):
        super(WavReplay, self).__init__()
        self.filename=filename
        self.frames_per_buffer=frames_per_buffer
        self.realtime=realtime
        self.CHANNELS=self._file.getnchannels()==1
        self.RATE=self._file.getframerate()
        self.SAMPLEWIDTH=self._file.getsampwidth()
        self.FORMAT=format_from_width[self.SAMPLEWIDTH]

    def readframes(self,n):
        return self._file.readframes(n)
        
    def start_process(self):
        self.t0=time.time()
        self._file=wave.open(self.filename, "rb")
        self._process
 
def FileReplay(filename, **kwargs):
    if filename.endswith("wav"):
        return WavReplay(filename, **kwargs)
    return RawReplay(filename, **kwargs)
