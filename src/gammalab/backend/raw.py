from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveRaw(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        super(SaveRaw, self).__init__()

        self.input_wire=RawWire()
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
        
        self.output=open(self.outputfile, 'wb')

    def process(self, data):
        self.output.write(data)

    def stop(self):
        self.output.close()
        ThreadService.stop(self)
