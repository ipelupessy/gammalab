from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveRaw(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
        
        self.output=open(self.outputfile, 'w')

    def _process_input(self, data):
        self.output.write(data)

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
