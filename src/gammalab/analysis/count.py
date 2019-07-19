from __future__ import print_function
import sys

from ..service import ReceivingService, ThreadService
from ..wire import PulseWire

class Count(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=PulseWire()
        self.all_pulses=[]
        
    def process(self, data):
        if len(data)>0:
            self.all_pulses.extend(data)
        total=len(self.all_pulses)
        cps=0
        cps10=0
        dt=0
        if total>0:
            dt=self.all_pulses[-1][0]-self.all_pulses[1][0]
            if dt>0:
                cps=total/dt
        if total>101:
            dt10=self.all_pulses[-1][0]-self.all_pulses[-100][0]
            if dt10>0:
                cps10=100./dt10
                
        print("time {0:f} total pulses {1:d}, cps: {2:f}, current cps (10%) {3:f} \r".format(dt, total, cps, cps10), end="")
        sys.stdout.flush()

    #~ def _process(self):
        #~ while not self.done:
            #~ try:
                #~ q=self.receive_input()
            #~ except Exception as ex:
                #~ q=None
            #~ if q is not None:
                #~ if not self.stopped:
                    #~ self._process_input(q)
            #~ else:
                #~ self.done=True
