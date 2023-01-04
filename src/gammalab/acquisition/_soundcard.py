from ..service import SourceService, ThreadService
from ..wire import FloatWire

import time

class SoundCard(ThreadService, SourceService):
    output_wire_class=FloatWire

    @staticmethod
    def devices():
        """ return dict with names and ids of sound devices for acquisition (aka microphones) """
        try:
            import soundcard
        except Exception as ex:
            raise Exception( f"import error: {str(ex)}")
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
        super().__init__()

    def start_process(self):
        global soundcard
        try:
            import soundcard
        except Exception as ex:
            self.print_message( f"import error: {str(ex)}")
        super().start_process()

    def _process(self):
        mic=soundcard.get_microphone(self.input_device_index or self.input_device_name)
        self.print_message( f"opening {str(mic)} for data acquisition")
        name=mic.name
        t0=time.time()
        total_samples=0
        with mic.recorder(samplerate=self.RATE, blocksize=self.frames_per_buffer, channels=self.CHANNELS) as recorder:
            while not self.stopped:    
                try:
                    _name=mic.name # this can raise exception if mic dissapears
                    assert _name==name # double check
                except:
                    raise Exception("Soundcard acquisition device possibly disconnected")

                try:
                    data=recorder.record(self.frames_per_buffer)
                    t_wall=time.time()-t0
                except Exception as ex:
                    self.print_message( f"error: {str(ex)}")
                    self.stopped=True
                if len(data)==0 or data is None:
                    self.print_message("no data")
                    self.stopped=True
                else:
                    data=dict(data=data.flatten(), wallclock_time=t_wall) # flatten because we have hardcoded nchannels=1
    
                if (not self.stopped and
                    data is not None):
                    self.send_output(data)
                    total_samples+=len(data["data"])
                
            self.send_output(None)
        t_wall=time.time()-t0
        t_sample=total_samples/self.RATE
        self.print_message(f"wallclock(s): {t_wall:6.2f}, sample time(s): {t_sample:6.2f},  difference: {100*(t_wall-t_sample)/t_wall:4.2f}%")

        self.stopped=True

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.CHANNELS
        wire.RATE=self.RATE
        wire.FORMAT=self.FORMAT
