from ..service import ThreadService, SourceService
from ..wire import FloatWire, Int16Wire

import time
import numpy
import wave

format_nbytes=dict(int16=2, float32=4)

class RawReplay(ThreadService, SourceService):
    output_wire_class=FloatWire
    def __init__(self, filename="data.raw", frames_per_buffer=1024, realtime=True, 
        sample_rate=48000, sample_format="float32"):
        super().__init__()
        self.CHANNELS=1
        self.RATE=sample_rate
        assert sample_format=="float32"
        self.FORMAT=sample_format
        self.filename=filename
        self.frames_per_buffer=frames_per_buffer
        self.realtime=realtime
        self.total_frames=0

    def output_protocol(self, wire):
        super().output_protocol(wire)      
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
    
    def readframes(self,n):
        return self._file.read(format_nbytes[self.FORMAT]*n)
    
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
        self.total_frames+=n
        if len(data)==0:
          self.print_message("End of file")
          self.stopped=True
          return None
        return dict(data=numpy.frombuffer(data, dtype=self.FORMAT), wallclock_time=self.total_frames/self.RATE)
        
    def start_process(self):
        self.t0=time.time()
        self.print_message(f"reading from {self.filename}")
        with open(self.filename, "rb") as self._file:
            super().start_process()


format_from_width={2 : "int16", 4 : "float32"}

class WavReplay(RawReplay):
    output_wire_class=Int16Wire
    def __init__(self, filename, frames_per_buffer=1024, realtime=True):
        super().__init__()
        self.filename=filename
        self.frames_per_buffer=frames_per_buffer
        self.realtime=realtime
        self._file=wave.open(self.filename, "rb")
        self.CHANNELS=1
        assert self._file.getnchannels()==1
        self.RATE=self._file.getframerate()
        self.SAMPLEWIDTH=self._file.getsampwidth()
        self.FORMAT=format_from_width[self.SAMPLEWIDTH]
        assert self.FORMAT=="int16"
        
    def readframes(self,n):
        return self._file.readframes(n)

    def start_process(self):
        self.t0=time.time()
        self.print_message(f"reading from {self.filename}")
        self._process()
        
    def cleanup(self):
        self._file.close()
        super().cleanup()

def FileReplay(filename, **kwargs):
    if filename.endswith("wav"):
        return WavReplay(filename, **kwargs)
    return RawReplay(filename, **kwargs)
