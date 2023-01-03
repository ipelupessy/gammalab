from ..service import ReceivingService, SourceService, ThreadService
from ..wire import RawWire, FloatWire, Int16Wire, NumpyWire

import numpy

class Identity(ThreadService, SourceService, ReceivingService):
    input_wire_class=RawWire
    output_wire_class=RawWire
    
    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT

    def process(self, data):
        return data

class Raw2Numpy(ThreadService, SourceService, ReceivingService):
    input_wire_class=RawWire
    output_wire_class=NumpyWire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT

    def process(self, data):
        return numpy.frombuffer(data,dtype=self.input_wire.FORMAT)

class Numpy2Raw(ThreadService, SourceService, ReceivingService):
    input_wire_class=NumpyWire
    output_wire_class=RawWire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT

    def process(self, data):
        return data.tobytes()


class Raw2Float(ThreadService, SourceService, ReceivingService):
    input_wire_class=RawWire
    output_wire_class=FloatWire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT="float32"

    def process(self, data):
        if self.input_wire.FORMAT=="float32":
          return numpy.frombuffer(data,dtype=self.input_wire.FORMAT)
        elif self.input_wire.FORMAT=="int16":
          data=numpy.frombuffer(data,dtype=self.input_wire.FORMAT)
          return data.astype("float32")/32768
        else:
          self.print_message("unknown data format in wire")
          return None

class Float2Raw(ThreadService, SourceService, ReceivingService):
    input_wire_class=FloatWire
    output_wire_class=RawWire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT

    def process(self, data):
        return data.tobytes()

class DownSampleMaxed(ThreadService, SourceService, ReceivingService):
    input_wire_class=FloatWire
    output_wire_class=FloatWire

    def __init__(self, factor=8):
        super().__init__()
        self.factor=factor

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.FORMAT=self.input_wire.FORMAT
        wire.RATE=self.input_wire.RATE/self.factor

    def process(self, data):
        return numpy.max(data.reshape(-1, self.factor),axis=1)

class Normalize(ThreadService, SourceService, ReceivingService):
    input_wire_class=FloatWire
    output_wire_class=FloatWire

    def __init__(self, baseline=0., scale=1.):
        super().__init__()
        self.scale=scale
        self.baseline=baseline

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT="float32"

    def process(self, data):
        return numpy.clip(self.scale*(data-self.baseline), -1.,1., dtype="float32")

class Float2Int16(ThreadService, SourceService, ReceivingService):
    input_wire_class=FloatWire
    output_wire_class=Int16Wire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT="int16"

    def process(self, data):
        if self.input_wire.FORMAT=="float32":
          return numpy.array(32767*data).astype("int16")
        elif self.input_wire.FORMAT=="int16":
          return data
        else:
          self.print_message("unknown data format in wire")
          return None
          
class Int162Raw(ThreadService, SourceService, ReceivingService):
    input_wire_class=Int16Wire
    output_wire_class=RawWire

    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT="int16"

    def process(self, data):
          return numpy.array(data).tobytes()
