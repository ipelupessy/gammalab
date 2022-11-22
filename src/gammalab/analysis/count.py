import sys
import pickle

from ..service import ReceivingService, ThreadService
from ..wire import PulseWire

class Count(ThreadService, ReceivingService):
    def __init__(self, outfile="count"):
        super(Count, self).__init__()
        self.input_wire=PulseWire()
        self.all_pulses=[]
        self.outfile=outfile
        
    def process(self, data):
        if len(data)>0:
            self.all_pulses.extend(data)
        total=len(self.all_pulses)
        cps=0
        cps10=0
        dt=0
        if total>0:
            dt=self.all_pulses[-1][0]-self.all_pulses[0][0]
            if dt>0:
                cps=total/dt
        if total>101:
            dt10=self.all_pulses[-1][0]-self.all_pulses[-100][0]
            if dt10>0:
                cps10=100./dt10
                
        message="t: {0:6.3g}, counts: {1:5.3e} | avg. cps: {2:5.2f}, current cps (10%) {3:5.2f}".format(dt, total, cps, cps10)
        self.print_message(message)
        
    def stop(self):
        if self.outfile is not None:
            f=open(self.outfile+".pkl","wb")
            pickle.dump(self.all_pulses,f)
            f.close()
        ThreadService.stop(self)
    
