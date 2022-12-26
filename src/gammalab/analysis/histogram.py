from ..service import ThreadService, SourceService, ReceivingService
from ..wire import PulseWire, HistogramWire

import numpy
import pickle

class AggregateHistogram(ThreadService,ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=HistogramWire
    def __init__(self, nchannels=100, vmin=0.003, vmax=1., outfile="histogram",
        histogram_mode="normal"):
        super(AggregateHistogram, self).__init__()

        self.vmin=vmin
        self.vmax=vmax
        self.nchannels=nchannels
        self.outfile=outfile
        self.histogram_mode=histogram_mode

    def get_proportional_bins(self):
        if self.vmin==0:
            raise Exception("For proportional bins, vmin cant be zero")
        fac=(self.vmax/self.vmin)**(1./self.nchannels)        
        bins=[]
        x=self.vmin
        while x<self.vmax:
            bins.append(x)
            x=x*fac
        bins[-1]=self.vmax
        
        return numpy.array(bins)
            

    def get_histogram(self, data):
        if self.histogram_mode=="normal":
            return numpy.histogram(data, bins=self.nchannels, 
                range=(self.vmin,self.vmax))
        if self.histogram_mode=="proportional":
            bins=self.get_proportional_bins()
            return numpy.histogram(data, bins=bins)

        raise Exception(f"Unknown histogram_mode {self.histogram_mode}")

    def start_process(self):
        self.hist, self.bins=self.get_histogram([])
        self.total_time=0
        super(AggregateHistogram, self).start_process()

    def output_protocol(self, wire):
        super(AggregateHistogram, self).output_protocol(wire)
        wire.nchannels=self.nchannels
        wire.vmin=self.vmin
        wire.vmax=self.vmax
        wire.unit=self.input_wire.unit
        wire.histogram_mode=self.histogram_mode

    def process(self, data):
        signal=[x[1] for x in data["pulses"]]
        hist, bins=self.get_histogram(signal)
        
        self.hist=self.hist+hist
        self.bins=bins
        self.total_time=data["total_time"]

        return self.outdata

    @property
    def outdata(self):
        return dict(hist=self.hist, bins=self.bins, total_time=self.total_time)        

    def cleanup(self):
        if self.outfile is not None:
            f=open(self.outfile+".pkl","wb")
            pickle.dump(self.outdata,f)
            f.close()
        super(AggregateHistogram, self).cleanup()
