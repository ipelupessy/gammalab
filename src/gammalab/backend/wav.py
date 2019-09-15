from ..service import ReceivingService, ThreadService
from ..wire import RawWire

import wave

class SaveWav(ThreadService, ReceivingService):
    def __init__(self, filename=None):
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()
        
        if filename is None:
            filename="data.wav"
        
        self.outputfile=filename
        
        self.output=wave.open(self.outputfile, 'wb')

    def start(self):
        self.output.setnchannels(1)
        if self.input_wire.FORMAT!="int16":
            raise Exception("Format to be saved in wav needs to be int16")
        self.output.setsampwidth(2)
        self.output.setframerate(self.input_wire.RATE)

        ThreadService.start(self)



    def process(self, data):
        self.output.writeframes(data)

    def stop(self):
        self.output.close()
        ThreadService.stop(self)
