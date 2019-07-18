from ..service import ReceivingService, ThreadService
from ..wire import PulseWire

class Count(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=PulseWire()
        self.all_pulses=[]
        
    def _process_input(self, data):
        if len(data)>0:
            self.all_pulses.extend(data)
            total=len(self.all_pulses)
            dt=self.all_pulses[-1][0]-self.all_pulses[1][0]
            cps=total/dt
            if dt>0:
                print("time %f total pulses %d, cps: %f"%(dt, total, cps))
            if total>101:
                dt=self.all_pulses[-1][0]-self.all_pulses[-100][0]
                cps=100./dt
                if dt>0:
                    print("time %f, current cps (+/-10 ): %f "%(dt, cps))


    def _process(self):
        while not self.done:
            try:
                q=self.receive_input()
            except Exception as ex:
                q=None
            if q is not None:
                if not self.stopped:
                    self._process_input(q)
            else:
                self.done=True
