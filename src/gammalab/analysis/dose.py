import sys
import pickle
import numpy

from ..service import ReceivingService, ThreadService, SourceService
from ..wire import PulseWire, CountWire
      
class DoseCount(ThreadService, ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=CountWire
    def __init__(self, outfile=None, runtime=None, interval=1., silent=False, detector_mass=None):
        super().__init__()
        self.outfile=outfile
        self.runtime=runtime
        self.tmax=2*interval
        self.tmin=0
        self.interval=interval
        self.total_count=0
        self.total_time=0
        self.recent_pulse_times=[] # all pulse times from last interval
        self.recent_pulse_energies=[] # all pulse energies of last interval
        self.silent=silent
        self.dose=0.
        self.detector_mass=detector_mass

    def connect_input(self, service):
        super().connect_input(service)
        assert self.input_wire.unit=="keV"
    
    @property
    def nbins(self):
        return int((self.tmax-self.tmin)/self.interval)
        
    def start_process(self):
        if self.detector_mass is None:
            self.print_message("detector mass not specified, assuming 0.01 kg")
            self.detector_mass=0.01
        self.factor=1000*1.6e-19/(self.detector_mass)*3600/1.e-6  # converts keV/s (calculated below) to J/kg/hr (=uSv/hr or rather uGy/hr)
        
        self.cps, self.tbins=numpy.histogram([], bins=self.nbins, 
            range=(self.tmin,self.tmax))
        self.dose_rate=numpy.histogram([], bins=self.nbins, 
            range=(self.tmin,self.tmax))[0]

        super().start_process() 
    
    def process(self, data):      

        self.total_time=data["total_time"]
        self.total_count+=len(data["pulses"])

        if self.tmax<self.total_time:
            self.tmax=self.tmax*2
        if self.runtime and self.tmax>self.runtime:
            self.tmax=self.runtime

        _cps=self.cps
        _dose_rate=self.dose_rate

        pulse_times=[d[0] for d in data["pulses"]]
        pulse_energies=[d[1] for d in data["pulses"]]
        self.recent_pulse_times.extend(pulse_times)
        self.recent_pulse_energies.extend(pulse_energies)
        self.recent_pulse_energies=[e for t,e in zip(self.recent_pulse_times, self.recent_pulse_energies) if t>self.total_time-self.interval]
        self.recent_pulse_times=[t for t in self.recent_pulse_times if t>self.total_time-self.interval]

        pulse_times=numpy.array(pulse_times)
        pulse_energies=numpy.array(pulse_energies)
        
        self.dose+=pulse_energies.sum()

        counts, self.tbins=numpy.histogram(pulse_times, bins=self.nbins, 
            range=(self.tmin,self.tmax))
        dose, dummy=numpy.histogram(pulse_times, bins=self.nbins, 
            range=(self.tmin,self.tmax), weights=pulse_energies)
        
        self.cps=counts/self.interval
        self.cps[0:len(_cps)]+=_cps

        self.dose_rate=dose/self.interval
        self.dose_rate[0:len(_dose_rate)]+=_dose_rate

        avgcps=self.total_count/(self.total_time)
        if self.total_time>0:
          cps=len(self.recent_pulse_times)/min(self.total_time, self.interval)
        else:
          cps=0

        avgdose_rate=self.factor*self.dose/self.total_time
        if self.total_time>0:
          dose_rate=self.factor*numpy.sum(self.recent_pulse_energies)/min(self.total_time, self.interval)
        else:
          dose_rate=0

        message=f"time: {self.total_time:.2f}, dose rate(uGy/hr): {dose_rate:5.2f}, average dr(uGy/hr): {avgdose_rate:5.2f}, total dose(uGy): {avgdose_rate*self.total_time/3600.:6.3f}"
        if not self.silent:
            self.print_message(message, end="\r")
        
        return self.outdata
    
    @property            
    def outdata(self):
        return dict(count_per_sec=self.cps, dose_rate=self.dose_rate, time_bins=self.tbins, total_time=self.total_time, interval=self.interval)
      
    def cleanup(self):
        if self.outfile is not None:
            outfile=self.outfile+".pkl"
            with open(outfile,"wb") as f:
                pickle.dump(self.outdata,f)
            self.print_message(f"Data written to {outfile}")
        super().cleanup()
