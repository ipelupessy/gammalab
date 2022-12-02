from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveRaw(ThreadService, ReceivingService):
    input_wire_class=RawWire
    def __init__(self, filename=None):
        super(SaveRaw, self).__init__()
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
        
        self.output=open(self.outputfile, 'wb')

    def process(self, data):
        self.output.write(data)

    def cleanup(self):
        self.output.close()
        super(SaveRaw, self).cleanup()
