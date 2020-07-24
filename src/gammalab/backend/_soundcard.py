import numpy
from ..service import ReceivingService, ThreadService
from ..wire import RawWire

try:
    import soundcard
    HAS_SOUNDCARD=True
except ImportError:
    HAS_SOUNDCARD=False

class SoundCardPlay(ThreadService, ReceivingService):
    def __init__(self, frames_per_buffer=2048, output_device_index=None, output_device_name=""):
        super(SoundCardPlay, self).__init__()
        if not HAS_SOUNDCARD:
          raise Exception("soundcard module not or not correctly installed")        
        self.input_wire=RawWire()
        self.frames_per_buffer=frames_per_buffer
        self.output_device_index=output_device_index
        self.output_device_name=output_device_name

    def connect_input(self,service):
        super(SoundCardPlay, self).connect_input(service)
        if self.input_wire.FORMAT != "float32":
            raise Exception("SoundCard playback only supports float32 format")

    def _process(self):
        speaker=soundcard.get_speaker(self.output_device_index or self.output_device_name)
        print(speaker)
        with speaker.player(samplerate=self.input_wire.RATE, blocksize=self.frames_per_buffer) as player:
            while not self.done:
                data=self.receive_input()
                if data is None:
                    self.done=True
                else:
                    data=numpy.frombuffer(data,dtype=self.input_wire.FORMAT)

                if not self.stopped and not self.done:
                    try:
                        player.play(data)
                    except Exception as ex:
                        self.print_message( "error: {0}".format(str(ex)))
                        self.done=True
        self.stopped=True
        
