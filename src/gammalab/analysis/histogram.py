from ..service import ThreadService, SourceService, ReceivingService
from ..wire import PulseWire, HistogramWire

import numpy
import pickle

class AggregateHistogram(ThreadService,ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=HistogramWire
    def __init__(self, nchannels=100, vmin=0.003, vmax=1., outfile="histogram",
        histogram_mode="normal"):
        super().__init__()

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
        for i in range(self.nchannels):
            bins.append(x)
            x=x*fac
        bins.append(self.vmax)
        
        return numpy.array(bins)

    def get_semi_proportional_bins(self):
        nextra=int(0.333*self.nchannels)
        if self.vmin==0:
            raise Exception("For proportional bins, vmin cant be zero")
        
        nchannels2=self.nchannels+nextra
        
        fac=(self.vmax/self.vmin)**(1./(nchannels2))        
        bins=[]
        x=self.vmin
        for i in range(nchannels2):
            bins.append(x)
            x=x*fac
        bins.append(self.vmax)
        bins=bins[nextra:]
        bins=numpy.array(bins)

        bins=bins/bins[0]*self.vmin
        l=bins[-1]-bins[0]
        bins=bins[0]+(bins-bins[0])/l*(self.vmax-self.vmin)

        return numpy.array(bins)


    def get_quadratic_bins(self):
        nn=2
        x=numpy.arange(self.nchannels+1)
        bins= self.vmax*( (x/self.nchannels)+(self.vmin/self.vmax)**(1./nn)) **nn / (1+(self.vmin/self.vmax)**(1/nn))**nn
        return bins
  
    def get_histogram(self, data):
        if self.histogram_mode=="normal":
            return numpy.histogram(data, bins=self.nchannels, 
                range=(self.vmin,self.vmax))
        if self.histogram_mode=="proportional":
            bins=self.get_proportional_bins()
            return numpy.histogram(data, bins=bins)
        if self.histogram_mode=="semiprop":
            bins=self.get_semi_proportional_bins()
            return numpy.histogram(data, bins=bins)
        if self.histogram_mode=="quadratic":
            bins=self.get_quadratic_bins()
            return numpy.histogram(data, bins=bins)


        raise Exception(f"Unknown histogram_mode {self.histogram_mode}")

    def start_process(self):
        self.hist, self.bins=self.get_histogram([])
        self.total_time=0
        super().start_process()

    def output_protocol(self, wire):
        super().output_protocol(wire)
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
        return dict(hist=self.hist, bins=self.bins, total_time=self.total_time, 
                    unit=self.input_wire.unit)        

    def cleanup(self):
        if self.outfile is not None:
            outfile=self.outfile+".pkl"
            with open(outfile,"wb") as f:
                pickle.dump(self.outdata,f)
            self.print_message(f"Data written to {outfile}")
        super().cleanup()
