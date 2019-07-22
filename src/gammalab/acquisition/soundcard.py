from ..service import SourceService
from ..wire import RawWire

import pyaudio

pyaudio_format=dict(float32=pyaudio.paFloat32)

class SoundCard(SourceService):
    def __init__(self, frames_per_buffer=2048):
        SourceService.__init__(self)
        self.CHANNELS=1
        self.RATE=48000
        self.FORMAT="float32"
        self.pyaudio=pyaudio.PyAudio()
        self.recorder=None
        self.frames_per_buffer=frames_per_buffer
        
    def output_protocol(self, wire):
        assert isinstance(wire, RawWire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
        
    def _callback(self, in_data, frame_count, time_info, status):
        self.send_output(in_data)
        return (None, pyaudio.paContinue)

    def start(self):
        self.recorder = self.pyaudio.open(
                format=pyaudio_format[self.FORMAT],
                channels=self.CHANNELS,
                rate=self.RATE,
                frames_per_buffer=self.frames_per_buffer,
                input=True,
                stream_callback=self._callback
                )
                
    def stop(self):
        if self.recorder:
            self.recorder.stop_stream()

    def close(self):
        if self.recorder:
            self.recorder.stop_stream()
            self.recorder.close()

        self.pyaudio.terminate()
