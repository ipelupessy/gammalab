from ..service import ReceivingService, SourceService, ThreadService
from ..wire import FloatWire, PulseWire

import numpy

class PulseDetection(ThreadService, SourceService, ReceivingService):
    def __init__(self, threshold=0.005, window=24*1024):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=FloatWire()
        self.threshold=threshold
        self.window=window

    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)

    def start(self):
        self.data=numpy.zeros(self.window, dtype=self.input_wire.FORMAT)
        self.ndata=0
        self.RATE=self.input_wire.RATE
        self.itime=0
        ThreadService.start(self)

    def detect_pulses(self):
        larger=self.data>=self.threshold
        smaller=self.data<self.threshold
        
        up=smaller[:-1]*larger[1:]
        down=larger[:-1]*smaller[1:]
        
        up=numpy.argwhere(up) 
        down=numpy.argwhere(down) 
        
        up=up[:,0]
        down=down[:,0]
                
        if larger[0]: # discard first down crossing edge
          down=down[1:]
        if larger[-1]: # discard last up crossing edge
          up=up[:-1]
        
        if len(up)!=len(down):
            raise Exception("at this point, number of up and down edges must be same")
       
        #~ assert numpy.all(up<down)
        #~ assert numpy.all(up[1:]>down[:-1])
        #~ print "number of pulses:", len(up)
        
        pulses=[]
        for start,end in zip(up,down)[:50]:
          if end-start>5:
            time=start/(1.*self.RATE)+self.itime
            amplitude=numpy.max(self.data[start:end])
            pulses.append((time,amplitude))
            
        self.itime+=self.window/(1.*self.RATE)
        return pulses

    def process(self, data):
        self.data[self.ndata:self.ndata+len(data)]=data
        self.ndata+=len(data)
        if self.ndata>=self.window:
            self.ndata=0
            return self.detect_pulses()
        return None
