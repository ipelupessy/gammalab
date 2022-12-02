from ..service import ThreadService, SourceService, ReceivingService
from ..wire import PulseWire, HistogramWire

import numpy
import pickle

class AggregateHistogram(ThreadService,ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=HistogramWire
    def __init__(self, nchannels=100, vmin=0, vmax=1., outfile="histogram"):
        super(AggregateHistogram, self).__init__()

        self.vmin=vmin
        self.vmax=vmax
        self.nchannels=nchannels
        self.outfile=outfile

        self.hist, self.bins=numpy.histogram([], bins=self.nchannels, 
            range=(self.vmin,self.vmax))

    def output_protocol(self, wire):
        super(AggregateHistogram, self).output_protocol(wire)
        wire.nchannels=self.nchannels
        wire.vmin=self.vmin
        wire.vmax=self.vmax
        wire.unit=self.input_wire.unit

    def process(self, data):
        signal=[x[1] for x in data]
        hist, bins=numpy.histogram(signal, bins=self.nchannels, 
            range=(self.vmin,self.vmax))
        
        self.hist=self.hist+hist

        return dict(hist=self.hist, bins=self.bins)

    def cleanup(self):
        if self.outfile is not None:
            f=open(self.outfile+".pkl","wb")
            pickle.dump((self.hist, self.bins),f)
            f.close()
        super(AggregateHistogram, self).cleanup()
