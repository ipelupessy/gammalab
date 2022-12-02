from ..service import SourceService, ThreadService
from ..wire import RawWire

class SoundCard(ThreadService, SourceService):
    output_wire_class=RawWire

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for acquisition (aka microphones) """
        try:
            import soundcard
        except Exception as ex:
            raise Exception( "import error: {0}".format(str(ex)))
        result=dict()
        for m in soundcard.all_microphones():
          result[m.name]=m.id
        return result
  
    def __init__(self, frames_per_buffer=2048, input_device_index=None, input_device_name="",
                 sample_rate=48000, sample_format="float32"):
        self.CHANNELS=1
        self.RATE=sample_rate
        if sample_format != "float32":
          raise Exception("SoundCard only supports float32 sample_format")
        self.FORMAT=sample_format
        self.frames_per_buffer=frames_per_buffer
        self.input_device_index=input_device_index
        self.input_device_name=input_device_name
        super(SoundCard, self).__init__()

    def _process(self):
        global soundcard
        try:
            import soundcard
        except Exception as ex:
            self.print_message( "import error: {0}".format(str(ex)))

        mic=soundcard.get_microphone(self.input_device_index or self.input_device_name)
        with mic.recorder(samplerate=self.RATE, blocksize=self.frames_per_buffer, channels=self.CHANNELS) as recorder:
            while not self.stopped:    
                try:
                    data=recorder.record(self.frames_per_buffer)
                except Exception as ex:
                    self.print_message( "error: {0}".format(str(ex)))
                    self.stopped=True
                if len(data)==0:
                    self.print_message("no data")
                    self.stopped=True
                else:
                    data=data.astype("float32").tobytes()
    
                if (not self.stopped and
                    data is not None):
                    self.send_output(data)
                
            self.send_output(None)
        self.stopped=True

    def output_protocol(self, wire):
        super(SoundCard, self).output_protocol(wire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
