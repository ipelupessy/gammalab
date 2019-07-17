from ..service import ReceivingService, SourceService, ThreadService
from ..wire import FloatWire, PulseWire

import numpy

class PulseDetection(ThreadService, SourceService, ReceivingService):
    def __init__(self, threshold=0.005, window=24*1024):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.threshold=threshold
        self.window=window

    def connect(self, wire):
        assert isinstance(wire, PulseWire)
        self.wires.append(wire)

    def connect_input(self, service):
        self.input_wire=FloatWire()
        service.connect(self.input_wire)
        self.CHANNELS=service.CHANNELS
        self.RATE=service.RATE
        self.FORMAT=service.FORMAT
        self.data=numpy.zeros(self.window, dtype=self.FORMAT)
        self.ndata=0

    def detect_pulses(self):
        larger=self.data>=self.threshold
        smaller=self.data<self.threshold
        
        up=larger[1:-1]*smaller[:-2]
        down=larger[1:-1]*smaller[2:]
        
        up=numpy.argwhere(up) + 1 #account for shift
        down=numpy.argwhere(down) + 2 # take 1 extra point
        
        up=up[:,0]
        down=down[:,0]
        
        if larger[0]: # discard first down crossing edge
          down=down[1:]
        if larger[-1]: # discard last up crossing edge
          up=up[:-1]
        
        if len(up)!=len(down):
            raise Exception("at this point, number of up and down edges must be same")
            
        print "number of pulses:", len(up)
        
        pulses=[]
        for start,end in zip(up,down)[:50]:
            time=start
            amplitude=numpy.max(self.data[start:end])
            pulses.append((time,amplitude))
            
        return pulses

    def _process_input(self, data):
        self.data[self.ndata:self.ndata+len(data)]=data
        self.ndata+=len(data)
        if self.ndata>=self.window:
            self.ndata=0
            return self.detect_pulses()
        return None

    def _process(self):
        while not self.done:
            try:
                inp=self.receive_input()
            except Exception as ex:
                inp=None
            if inp is not None:
                if not self.stopped:
                    out=self._process_input(inp)
                    if out is not None:
                        self.send_output(out)
            else:
                self.done=True
