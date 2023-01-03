from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveRaw(ThreadService, ReceivingService):
    input_wire_class=RawWire
    def __init__(self, filename=None):
        super().__init__()
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
    
    def start_process(self):    
        with open(self.outputfile, 'wb') as self.output:
            super().start_process()

    def process(self, data):
        self.output.write(data)
