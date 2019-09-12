from ..service import ReceivingService, SourceService, ThreadService
from ..wire import RawWire, FloatWire

import numpy

class Identity(ThreadService, SourceService, ReceivingService):
    def __init__(self):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()

    def output_protocol(self, wire):
        assert isinstance(wire, RawWire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT        

    def process(self, data):
        return data

class Raw2Numpy(ThreadService, SourceService, ReceivingService):
    def __init__(self):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()

    def output_protocol(self, wire):
        assert isinstance(wire, FloatWire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT        

    def process(self, data):
        return numpy.frombuffer(data,dtype=self.input_wire.FORMAT)

class Raw2Float(ThreadService, SourceService, ReceivingService):
    def __init__(self):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()

    def output_protocol(self, wire):
        assert isinstance(wire, FloatWire)
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

class DownSampleMaxed(ThreadService, SourceService, ReceivingService):
    def __init__(self, factor=8):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=FloatWire()
        self.factor=factor

    def output_protocol(self, wire):
        assert isinstance(wire, FloatWire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.FORMAT=self.input_wire.FORMAT
        wire.RATE=self.input_wire.RATE/self.factor

    def process(self, data):
        return numpy.max(data.reshape(-1, self.factor),axis=1)
