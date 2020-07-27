from ..service import SourceService, ThreadService
from ..wire import RawWire

try:
    import soundcard
    HAS_SOUNDCARD=True
except ImportError:
    HAS_SOUNDCARD=False

class SoundCard(ThreadService, SourceService):

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for acquisition (aka microphones) """
        result=dict()
        if HAS_SOUNDCARD:
          for m in soundcard.all_microphones():
            result[m.name]=m.id
        return result
  
    def __init__(self, frames_per_buffer=2048, input_device_index=None, input_device_name="",
                 sample_rate=48000, sample_format="float32"):
        if not HAS_SOUNDCARD:
          raise Exception("soundcard module not or not correctly installed")        
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
        mic=soundcard.get_microphone(self.input_device_index or self.input_device_name)
        with mic.recorder(samplerate=self.RATE, blocksize=self.frames_per_buffer, channels=self.CHANNELS) as recorder:
            while not self.done:    
                if not self.stopped and not self.done:
                    try:
                        data=recorder.record(self.frames_per_buffer)
                    except Exception as ex:
                        self.print_message( "error: {0}".format(str(ex)))
                        self.done=True
                    if len(data)==0:
                        self.print_message("no data")
                        self.done=True
                    else:
                        data=data.astype("float32").tobytes()
    
                if (not self.stopped and 
                    not self.done and
                    data is not None):  
                    self.send_output(data)
                
            self.send_output(None)
        self.stopped=True

    def output_protocol(self, wire):
        assert isinstance(wire, RawWire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
