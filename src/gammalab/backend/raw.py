from ..service import ReceivingService, ThreadService
from ..wire import FloatWire

class SaveRaw(ThreadService, ReceivingService):
    input_wire_class=FloatWire
    def __init__(self, filename=None):
        super().__init__()
        
        if filename is None:
            filename="data.raw"
        
        self.outputfile=filename
    
    def start_process(self):    
        with open(self.outputfile, 'wb') as self.output:
            super().start_process()
        self.print_message(f"done writing to {self.outputfile}")

    def process(self, data):
        self.output.write(data["data"].tobytes())
