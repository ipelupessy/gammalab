from ..service import ThreadService, SourceService, ReceivingService
from ..wire import PulseWire, HistogramWire

import time
import numpy
import pickle

class AggregateHistogram(ThreadService,ReceivingService, SourceService):
    def __init__(self, nchannels=100, vmin=0, vmax=1., outfile="histogram"):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=PulseWire()

        self.vmin=vmin
        self.vmax=vmax
        self.nchannels=nchannels
        self.outfile=outfile

        self.hist, self.bins=numpy.histogram([], bins=self.nchannels, 
            range=(self.vmin,self.vmax))

    def output_protocol(self, wire):
        assert isinstance(wire, HistogramWire)
        wire.nchannels=self.nchannels
        wire.vmin=self.vmin
        wire.vmax=self.vmax

    def process(self, data):
        hist, bins=numpy.histogram(data, bins=self.nchannels, 
            range=(self.vmin,self.vmax))
        
        self.hist=self.hist+hist

        return dict(hist=self.hist, bins=self.bins)

    def stop(self):
        if self.outfile is not None:
            f=open(self.outfile+".pkl","wb")
            pickle.dump((self.hist, self.bins),f)
            f.close()
        ThreadService.stop(self)
  
