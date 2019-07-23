from ..service import ReceivingService
from ..wire import RawWire

import pyaudio

pyaudio_format=dict(float32=pyaudio.paFloat32)
pyaudio_nbytes=dict(float32=4)

class Playback(ReceivingService):
    def __init__(self, frames_per_buffer=2048):
        ReceivingService.__init__(self)
        self.input_wire=RawWire()      
        self.pyaudio=pyaudio.PyAudio()
        self.player=None
        self.frames_per_buffer=frames_per_buffer

    def _callback(self, in_data, frame_count, time_info, status):
        data=self.receive_input(block=False)
        if data is None:
            print("playback buffer underrun")
            data=bytes(0)*pyaudio_nbytes[self.input_wire.FORMAT]*frame_count
        return (data, pyaudio.paContinue)

    def start(self):
        self.player = self.pyaudio.open(
                format=pyaudio_format[self.input_wire.FORMAT],
                channels=self.input_wire.CHANNELS,
                rate=self.input_wire.RATE,
                frames_per_buffer=self.frames_per_buffer,
                output=True,
                stream_callback=self._callback
                )
                
    def stop(self):
        if self.player:
            self.player.stop_stream()

    def close(self):
        if self.player:
            self.player.stop_stream()
            self.player.close()

        self.pyaudio.terminate()
        
