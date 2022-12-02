from ..service import ReceivingService, ThreadService
from ..wire import RawWire

class SaveWav(ThreadService, ReceivingService):
    input_wire_class=RawWire
    
    def __init__(self, filename=None):
        super(SaveWav, self).__init__()

        if filename is None:
            filename="data.wav"
        
        self.outputfile=filename
        
    def start_process(self):
        global wav
        
        try:
          import wav
        except Exception as ex:
            self.print_message( "import error: {0}".format(str(ex)))

        self.output=wave.open(self.outputfile, 'wb')
        self.output.setnchannels(1)
        if self.input_wire.FORMAT!="int16":
            raise Exception("Format to be saved in wav needs to be int16")
        self.output.setsampwidth(2)
        self.output.setframerate(self.input_wire.RATE)
        
        super(SaveWav, self).start_process()

    def process(self, data):
        self.output.writeframes(data)

    def cleanup(self):
        self.output.close()
