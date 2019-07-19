from ..service import ReceivingService, SourceService, ThreadService
from ..wire import RawWire, FloatWire

import numpy

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
        wire.FORMAT=self.input_wire.FORMAT        

    def process(self, data):
        return numpy.frombuffer(data,dtype=self.input_wire.FORMAT)

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
