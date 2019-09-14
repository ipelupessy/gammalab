from ..service import ReceivingService, SourceService, ThreadService
from ..wire import FloatWire, PulseWire

from functools import partial
import numpy

try:
    import scipy
    from scipy.optimize import curve_fit
    HAS_SCIPY=True    
except:
    HAS_SCIPY=False
    
class PulseDetection(ThreadService, SourceService, ReceivingService):
    def __init__(self, threshold=0.005, window=24*1024, debug=False):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=FloatWire()
        self.threshold=threshold
        self.window=window
        self.debug=debug
        self._x=numpy.arange(window)

    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)
        wire._debug=self.debug

    def start(self):
        self.data=numpy.zeros(self.window, dtype=self.input_wire.FORMAT)
        self.ndata=0
        self.RATE=self.input_wire.RATE
        self.itime=0
        ThreadService.start(self)
  
    def amplitude_and_quality(self, start,end):
        return numpy.max(self.data[start:end]),0

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
        for start,end in zip(up,down):
          if end-start>5:
            time=start/(1.*self.RATE)+self.itime
            try:
              amplitude, sigma=self.amplitude_and_quality(start,end)
            except:
              self.print_message("detection error")
              raise
              continue
            
            width=end-start

            if self.debug:
                pulse=self.data[max(start-5,0):end+15].copy()
                pulses.append((time,amplitude, width, sigma, pulse))
            else:
                pulses.append((time,amplitude, width, sigma))

        self.itime+=self.window/(1.*self.RATE)
        return pulses

    def process(self, data):
        outdata=[]
        while len(data)>0:
            start=self.ndata
            end=min(self.window,start+len(data))
            self.data[start:end]=data[:end-start]
            data=data[end-start:]
            self.ndata=end
            if self.ndata>=self.window:
                outdata.extend(self.detect_pulses())
                self.ndata=0
        
        return outdata or None


def pulse(x, A, x0,  y, tau):
        return y+(x>=x0)*A*(x-x0)**2*numpy.exp(-(x/tau))+(x<x0)*0.


class FittedPulseDetection(PulseDetection):
    def __init__(self, threshold=0.005, window=24*1024, debug=False):
        if not HAS_SCIPY:
            raise Exception("pulse fitting needs Scipy...")

        PulseDetection.__init__(self, threshold, window, debug)

        self.print_message("assumes very specific pulse shape, x**2 exp(-x/tau)")


    def _fit_pulse(self, x, yp):
    
        sigma=0.0035
    
        A_=numpy.max(yp) # initial parameters
        x0_=4.5
        tau=2.7247*self.input_wire.RATE/48000.
        
        template=partial(pulse, y=0., tau=tau)
        
        a=(yp<0.95) * (yp>A_/5.) # select range
        x_=x[a]
        yp_=yp[a]
        
        sigma_=sigma*numpy.ones_like(x_) # weights
      
        (A,x0),cov=curve_fit(template, x_,yp_, p0=(A_,x0_), sigma=sigma_)
          
        AA=A*numpy.exp(-x0/tau)
        e=4*AA*tau**2*numpy.exp(-2.) # peak value
    
        p_=template(x_,A,x0)
        sigma_=numpy.sum((p_-yp_)**2)/len(yp_)
        sigma_=sigma_**0.5 / sigma # normalized mean error
    
        return e, sigma_
  
    def amplitude_and_quality(self, start,end):
        data=self.data[max(start-5,0):end+15]
        return self._fit_pulse(self._x[:len(data)], data)
