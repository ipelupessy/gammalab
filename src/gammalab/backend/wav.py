import wave
try:
    from queue import Queue
except:
    from Queue import Queue

class SaveWav(object):
    def __init__(self, service, filename=None):
        if filename is None:
            filename="data.wav"
        self.input_queue=Queue() # maxsize?
        
        self.outputfile=filename
        
        try:
          service.connect(self.input_queue)
          self.CHANNELS=device.CHANNELS
          self.RATE=device.RATE
          self.FORMAT=device.FORMAT
        except:
          raise Exception("trying to connect incompatible services")

        self.output=wave.open(self.outputfile, 'w')
        self.output.setnchannels(self.CHANNELS)
        self.output.setframerate(self.RATE)
        self.output.setsampwidth()

    def 
