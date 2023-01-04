from ..service import ReceivingService, ThreadService
from ..wire import Int16Wire

class SaveWav(ThreadService, ReceivingService):
    input_wire_class=Int16Wire
    
    def __init__(self, filename=None):
        super().__init__()

        if filename is None:
            filename="data.wav"
        
        self.outputfile=filename
        
    def start_process(self):
        global wave
        
        try:
          import wave
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")

        with wave.open(self.outputfile, 'wb') as self.output:
            self.output.setnchannels(1)
            self.output.setsampwidth(2)
            self.output.setframerate(self.input_wire.RATE)
            
            super().start_process()
        self.print_message(f"done writing to {self.outputfile}")

    def process(self, data):
        self.output.writeframes(data["data"].tobytes())
                
