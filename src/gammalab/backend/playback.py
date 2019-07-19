from ..service import ReceivingService
from ..wire import RawWire

import pyaudio

pyaudio_format=dict(float32=pyaudio.paFloat32)

class Playback(ReceivingService):
    def __init__(self):
        ReceivingService.__init__(self)
        self.input_wire=RawWire()      
        self.pyaudio=pyaudio.PyAudio()
        self.player=None

    def _callback(self, in_data, frame_count, time_info, status):
        data=self.receive_input(block=False)
        if data is None:
            print("playback buffer underrun")
            data=bytes(0)*4096
        return (data, pyaudio.paContinue)

    def start(self):
        self.player = self.pyaudio.open(
                format=pyaudio_format[self.input_wire.FORMAT],
                channels=self.input_wire.CHANNELS,
                rate=self.input_wire.RATE,
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
