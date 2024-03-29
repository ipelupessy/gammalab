from ..service import ReceivingService, SourceService, ThreadService
from ..wire import FloatWire, PulseWire

from functools import partial
import numpy
import pickle
    
class PulseDetection(ThreadService, SourceService, ReceivingService):
    input_wire_class=FloatWire
    output_wire_class=PulseWire
    def __init__(self, threshold=0.005, window=24*1024, emit_pulse_shapes=False, outfile=None):
        super().__init__()
        self.threshold=threshold
        self.window=window
        self.emit_pulse_shapes=emit_pulse_shapes
        self._x=numpy.arange(window)
        self.outfile=outfile
        self.all_pulses=[]

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire._emit_pulse_shapes=self.emit_pulse_shapes
        wire.unit="raw value"

    def start_process(self):
        self.data=numpy.zeros(self.window, dtype=self.input_wire.FORMAT)
        self.ndata=0
        self.RATE=self.input_wire.RATE
        self.itime=0
        self.dtime=self.window/(1.*self.RATE)
        self.wallclock_time=0
        super().start_process()
  
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
            except Exception as ex:
              self.print_message("Pulse detection error condition: %s"%str(ex))
            
            width=end-start

            if self.emit_pulse_shapes:
                pulse=self.data[max(start-5,0):end+15].copy()
                pulses.append((time,amplitude, width, sigma, pulse))
            else:
                pulses.append((time,amplitude, width, sigma))

        return pulses

    def process(self, data):
        self.wallclock_time=data["wallclock_time"]
        data=data["data"]
        detect_ran=False
        pulses=[]
        dtime=0.
        while len(data)>0:
            start=self.ndata
            end=min(self.window,start+len(data))
            self.data[start:end]=data[:end-start]
            data=data[end-start:]
            self.ndata=end

            # if detection buffer filled, run detection
            if self.ndata>=self.window:
                pulses.extend(self.detect_pulses())
                detect_ran=True

                #update itime and dtime
                self.itime+=self.dtime
                dtime+=self.dtime
                
                self.ndata=0

        if self.outfile is not None:
            self.all_pulses.extend(pulses)

        if detect_ran:
            result=dict(pulses=pulses, total_time=self.itime, dtime=dtime, rate=self.RATE, wallclock_time=self.wallclock_time)
        else:
            result=None # do not send data if detection did not run
       
        return result

    @property            
    def outdata(self):
        return dict(pulses=self.all_pulses, total_time=self.itime, rate=self.RATE, wallclock_time=self.wallclock_time)

    def cleanup(self):
        if self.outfile is not None:
            outfile=self.outfile+".pkl"
            with open(outfile,"wb") as f:
                pickle.dump(self.outdata,f)
            self.print_message(f"Data written to {outfile}")
        super().cleanup()


def pulse(x, A, x0,  y, tau):
        return y+(x>=x0)*A*(x-x0)**2*numpy.exp(-(x/tau))+(x<x0)*0.


class FittedPulseDetection(PulseDetection):
    """ 
    detects pulses and determines amplitude by fitting a predifined 
    pulse shape. x**2*exp(-x/tau).

    In principle there could be two reasons to use fitted pulse shapes: in 
    case the signal is undersampled the maximum can fall between two 
    samples or if the signal saturates the ADC and the maximum can still be 
    recovered by fitting the rising and falling edges. 

    """
    def __init__(self, threshold=0.005, window=24*1024, emit_pulse_shapes=False,outfile=None, 
                  fit_threshold=0., signal_noise=0.0035, pulse_decay_time=2.7247/48000):

        super().__init__(threshold=threshold, 
                                                   window=window, 
                                                   emit_pulse_shapes=emit_pulse_shapes,
                                                   outfile=outfile)

        self.print_message("currently assumes very specific pulse shape, x**2 exp(-x/tau)")

        self.fit_threshold=fit_threshold
        self.sigma=signal_noise
        self.pulse_decay_time=pulse_decay_time

    def _fit_pulse(self, x, yp):
        global scipy, curve_fit
        
        A_=numpy.max(yp) # initial amplitude
        x0_=4.5 # initial timeshift
        tau=self.pulse_decay_time*self.input_wire.RATE
        
        template=partial(pulse, y=0., tau=tau) # fix base level (=0) and decay time
        
        a=(yp<0.95) * (yp>A_/5.) # select range
        x_=x[a]
        yp_=yp[a]
        
        sigma_=self.sigma*numpy.ones_like(x_) # weights
      
        (A,x0),cov=curve_fit(template, x_,yp_, p0=(A_,x0_), sigma=sigma_)
          
        AA=A*numpy.exp(-x0/tau)
        e=4*AA*tau**2*numpy.exp(-2.) # peak value
    
        p_=template(x_,A,x0)
        sigma_=numpy.sum((p_-yp_)**2)/len(yp_)
        sigma_=sigma_**0.5 / self.sigma # normalized mean error
    
        return e, sigma_
  
    def amplitude_and_quality(self, start,end):
        data=self.data[max(start-5,0):end+15]
        max_data=numpy.max(self.data[start:end])
        if max_data>self.fit_threshold:
            try:
                return self._fit_pulse(self._x[:len(data)], data)
            except Exception as ex:
                self.print_message("Fitted pulse detection error: %s"%str(ex))
                return max_data,0.
        else:
            return max_data,0.

    def start_process(self):
        global scipy, curve_fit
        
        try:
            import scipy
            from scipy.optimize import curve_fit
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")
            #~ self.stopped=True
            #~ self.done=True

        super().start_process()
