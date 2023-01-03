import sys
import pickle
import numpy

from ..service import ReceivingService, ThreadService, SourceService
from ..wire import PulseWire, CountWire
      
class Count(ThreadService, ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=CountWire
    def __init__(self, outfile=None, runtime=None, interval=1., silent=False):
        super().__init__()
        self.outfile=outfile
        self.runtime=runtime
        self.tmax=10
        self.tmin=0
        self.interval=interval
        self.total_count=0
        self.total_time=0
        self.recent_pulse_times=[] # all pulse times from last interval
        self.silent=silent
    
    @property
    def nbins(self):
        return int((self.tmax-self.tmin)/self.interval)
        
    def start_process(self):
        self.cps, self.tbins=numpy.histogram([], bins=self.nbins, 
            range=(self.tmin,self.tmax))
        super().start_process() 
    
    def process(self, data):      

        self.total_time=data["total_time"]
        self.total_count+=len(data["pulses"])

        if self.tmax<self.total_time:
            self.tmax=self.tmax*1.5
        if self.runtime and self.tmax>self.runtime:
            self.tmax=self.runtime

        _cps=self.cps

        pulse_times=numpy.array([d[0] for d in data["pulses"]])
        self.recent_pulse_times.extend(pulse_times)
        self.recent_pulse_times=[t for t in self.recent_pulse_times if t>self.total_time-self.interval]
        pulse_times=numpy.array(pulse_times)


        counts, self.tbins=numpy.histogram(pulse_times, bins=self.nbins, 
            range=(self.tmin,self.tmax))

        self.cps=counts/self.interval
        self.cps[0:len(_cps)]+=_cps

        avgcps=self.total_count/(self.total_time)
        if self.total_time>0:
          cps=len(self.recent_pulse_times)/min(self.total_time, self.interval)
        else:
          cps=0

        message=f"time: {self.total_time:7.2f} | counts: {self.total_count:5.3e} | "\
                f"average cps: {avgcps:5.2f} | current cps: {cps:5.2f}"
        if not self.silent:
            self.print_message(message)
        
        return self.outdata
    
    @property            
    def outdata(self):
        return dict(count_per_sec=self.cps, time_bins=self.tbins, total_time=self.total_time, interval=self.interval)
      
                
    def cleanup(self):
        if self.outfile is not None:
            outfile=self.outfile+".pkl"
            with open(outfile,"wb") as f:
                pickle.dump(self.outdata,f)
            self.print_message(f"Data written to {outfile}")
        super().cleanup()
