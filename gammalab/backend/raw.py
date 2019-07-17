from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveRaw(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
        
        self.output=open(self.outputfile, 'w')

    def connect_input(self, service):
        self.input_wire=RawWire()
        service.connect(self.input_wire)
        self.CHANNELS=service.CHANNELS
        self.RATE=service.RATE
        self.FORMAT=service.FORMAT

    def _process_input(self, data):
        self.output.write(data)

    def _process(self):
        while not self.done:
            try:
                q=self.receive_input()
            except Exception as ex:
                q=None
            if q:
                if not self.stopped:
                    self._process_input(q)
            else:
                self.done=True
