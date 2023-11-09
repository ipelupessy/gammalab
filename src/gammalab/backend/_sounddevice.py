import numpy
from ..service import ReceivingService, ThreadService
from ..wire import FloatWire

class SoundDevicePlay(ThreadService, ReceivingService):

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for playback (aka speakers) """
        try:
            import sounddevice
        except Exception as ex:
            raise Exception( f"import error: {str(ex)}")
        result=dict()
        for m in sounddevice.query_devices():
          if m["max_output_channels"]>0:
              result[m["name"]]=m["index"]
        return result

    input_wire_class=FloatWire

    def __init__(self, frames_per_buffer=2048, output_device_index=None, output_device_name=""):
        self.frames_per_buffer=frames_per_buffer
        self.output_device_index=output_device_index
        self.output_device_name=output_device_name
        self.CHANNELS=1
        super().__init__()

    def start_process(self):
        global sounddevice
        try:
            import sounddevice
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")
        super().start_process()

    def _process(self):            
        stream=sounddevice.OutputStream(
          samplerate=self.input_wire.RATE, blocksize=self.frames_per_buffer, channels=self.CHANNELS,
          device=self.output_device_index or self.output_device_name,
          dtype="float32"
          )
        name=sounddevice.query_devices(stream.device)["name"]  
        self.print_message( f"opening {name} for audio output")
        stream.start()
        while not self.stopped:
            data=self.receive_input()
            if data is None:
                self.stopped=True
            else:
                data=data["data"]

            if not self.stopped:
                try:
                    underflowed=stream.write(data)
                except Exception as ex:
                    self.print_message( f"error: {str(ex)}")
                    self.stopped=True

        stream.stop()
        self.stopped=True

