from ..service import SourceService, ThreadService
from ..wire import FloatWire

import numpy
import time
from contextlib import contextmanager
import signal

@contextmanager
def timeout(duration, message):
    def timeout_handler(signum, frame):
        raise TimeoutError(message)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)


class SoundDevice(ThreadService, SourceService):
    output_wire_class=FloatWire

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for acquisition (aka microphones) """
        try:
            import sounddevice
        except Exception as ex:
            raise Exception( f"import error: {str(ex)}")
        result=dict()
        for m in sounddevice.query_devices():
          if m["max_input_channels"]>0:
              result[m["name"]]=m["index"]
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
        super().__init__()

    def start_process(self):
        global sounddevice
        try:
            import sounddevice
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")
        super().start_process()

    def _process(self):
        stream=sounddevice.InputStream(
          samplerate=self.RATE, blocksize=self.frames_per_buffer, channels=self.CHANNELS,
          device=self.input_device_index or self.input_device_name,
          dtype="float32"
          )
        name=sounddevice.query_devices(stream.device)["name"]
        self.print_message( f"opening {name} for data acquisition")
        t0=time.time()
        total_samples=0
        stream.start()
        buffer=numpy.zeros(self.frames_per_buffer,dtype=numpy.float32)
        while not self.stopped:    
            try:
                _name=sounddevice.query_devices(name)["name"] # this can raise exception if device dissapears
                assert _name==name # double check
            except:
                raise Exception("Soundcard acquisition device possibly disconnected")

            buffer[:]=0
            try:
                frames_read=0
                with timeout(1,"timeout on data acquisition, possible soundcard disconnect"):
                    while frames_read<self.frames_per_buffer:
                      available=stream.read_available
                      request=min(available, self.frames_per_buffer-frames_read)
                      if request>0:
                          _data, overflowed=stream.read(request)
                          buffer[frames_read:frames_read+request]=_data[:,0] # flatten because we have hardcoded nchannels=1
                          frames_read+=request
                      time.sleep(self.frames_per_buffer/self.RATE/2)
                
                t_wall=time.time()-t0
                if overflowed:
                    self.print_message("data acquisition overflow")
            except Exception as ex:
                self.print_message( f"error: {str(ex)}")
                self.stopped=True
            if frames_read==0:
                self.print_message("no data")
                self.stopped=True
            else:
                data=dict(data=buffer.copy(), wallclock_time=t_wall)

            if (not self.stopped and
                data is not None):
                self.send_output(data)
                total_samples+=len(data["data"])

        self.send_output(None)
        t_wall=time.time()-t0
        t_sample=total_samples/self.RATE
        self.print_message(f"wallclock(s): {t_wall:6.2f}, sample time(s): {t_sample:6.2f},  difference: {100*(t_wall-t_sample)/t_wall:4.2f}%")

        stream.stop()
        self.stopped=True

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
