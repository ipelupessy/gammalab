from ..service import SourceService
from ..wire import RawWire

try:
    import pyaudio
    HAS_PYAUDIO=True

    pyaudio_format=dict(int16=pyaudio.paInt16, float32=pyaudio.paFloat32)
except ImportError:
    HAS_PYAUDIO=False


class PyAudio(SourceService):
    output_wire_class=RawWire
    def __init__(self, frames_per_buffer=2048, input_device_index=None, 
                 sample_rate=48000, sample_format="float32"):
        if not HAS_PYAUDIO:
          raise Exception("pyaudio module not or not correctly installed")
        self.CHANNELS=1
        self.RATE=sample_rate
        self.FORMAT=sample_format
        self.pyaudio=pyaudio.PyAudio()
        self.recorder=None
        self.frames_per_buffer=frames_per_buffer
        self.input_device_index=input_device_index
        super(PyAudio, self).__init__()
        
    def output_protocol(self, wire):
        super(PyAudio, self).output_protocol(wire)      
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
        
    def _callback(self, in_data, frame_count, time_info, status):
        self.send_output(in_data)
        if status!=0:
            self.print_message("status = {0}".format(status))
        return (None, pyaudio.paContinue)

    def start(self):
        self.recorder = self.pyaudio.open(
                format=pyaudio_format[self.FORMAT],
                channels=self.CHANNELS,
                rate=self.RATE,
                frames_per_buffer=self.frames_per_buffer,
                input=True,
                stream_callback=self._callback,
                input_device_index=self.input_device_index
                )
                
    def stop(self):
        if self.recorder:
            self.recorder.stop_stream()

    def close(self):
        if self.recorder:
            self.recorder.stop_stream()
            self.recorder.close()

        self.pyaudio.terminate()
