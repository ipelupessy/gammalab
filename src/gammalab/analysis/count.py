import sys
import pickle

from ..service import ReceivingService, ThreadService, SourceService
from ..wire import PulseWire, CountWire

class Count(ThreadService, ReceivingService, SourceService):
    input_wire_class=PulseWire
    output_wire_class=CountWire
    def __init__(self, outfile=None):
        super(Count, self).__init__()
        self.outfile=outfile
        self.count=[]
        self.time=[]
        self.dtime=[]
        self.total_count=0
    
    def get_current_cps(self):
        """ get a low noise (10%) estimate of current cps """
        
        current_time=self.time[-1]+self.dtime[-1]/2
        running=0
        i=len(self.count)
        while running<100 and i>0:
            i-=1
            running+=self.count[i]
        prev_time=self.time[i]-self.dtime[i]/2
        
        if (current_time-prev_time)>0:
            cps10=running/(current_time-prev_time)
        else:
            cps10=0
            
        return cps10

    def process(self, data):      
        time=data["total_time"]-data["dtime"]/2. # centered time
        current_time=data["total_time"] 
        dtime=data["dtime"]
        count=len(data["pulses"])
        total_count=self.total_count+count
                        
                        
        self.time.append(time)
        self.dtime.append(dtime)        
        self.count.append(count)
        self.total_count=total_count

        start_time=self.time[0]-self.dtime[0]/2

        cps=total_count/(current_time-start_time)
        cps10=self.get_current_cps()
                
        message="time: {0:6.3g} | counts: {1:5.3e} | average cps: {2:5.2f} | current cps: {3:5.2f}".format(
                 current_time, total_count, cps, cps10)
        self.print_message(message)
        
        return time,cps10
                
    def cleanup(self):
        if self.outfile is not None:
            f=open(self.outfile+".pkl","wb")
            pickle.dump((self.time, self.dtime, self.count),f)
            f.close()
        super(Count, self).cleanup()
      
