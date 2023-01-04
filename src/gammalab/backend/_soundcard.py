import numpy
from ..service import ReceivingService, ThreadService
from ..wire import FloatWire

class SoundCardPlay(ThreadService, ReceivingService):

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for playback (aka speakers) """
        result=dict()
        try:
            import soundcard
        except Exception as ex:
            raise Exception( f"import error: {str(ex)}")

        for m in soundcard.all_speakers():
          result[m.name]=m.id
        return result

    input_wire_class=FloatWire

    def __init__(self, frames_per_buffer=2048, output_device_index=None, output_device_name=""):
        self.frames_per_buffer=frames_per_buffer
        self.output_device_index=output_device_index
        self.output_device_name=output_device_name
        super().__init__()

    def start_process(self):
        global soundcard
        try:
            import soundcard
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")
        super().start_process()

    def _process(self):            
        speaker=soundcard.get_speaker(self.output_device_index or self.output_device_name)
        self.print_message( f"opening {str(speaker)} for audio output")

        with speaker.player(samplerate=self.input_wire.RATE, blocksize=self.frames_per_buffer) as player:
            while not self.stopped:
                data=self.receive_input()
                if data is None:
                    self.stopped=True
                else:
                    data=data["data"]

                if not self.stopped:
                    try:
                        player.play(data)
                    except Exception as ex:
                        self.print_message( f"error: {str(ex)}")
                        self.stopped=True
        self.stopped=True

