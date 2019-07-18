from ..service import ReceivingService, SourceService, ThreadService
from ..wire import RawWire, FloatWire

import numpy

class Raw2Float(ThreadService, SourceService, ReceivingService):
    def __init__(self):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=RawWire()

    def connect(self, wire):
        assert isinstance(wire, FloatWire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.RATE=self.input_wire.RATE
        wire.FORMAT=self.input_wire.FORMAT        
        self.wires.append(wire)

    def connect_input(self, service):
        service.connect(self.input_wire)

    def _process_input(self, data):
        return numpy.frombuffer(data,dtype=self.input_wire.FORMAT)

    def _process(self):
        while not self.done:
            try:
                inp=self.receive_input()
            except Exception as ex:
                inp=None
            if inp is not None:
                if not self.stopped:
                    out=self._process_input(inp)
                    self.send_output(out)
            else:
                self.done=True

class DownSampleMaxed(ThreadService, SourceService, ReceivingService):
    def __init__(self, factor=8):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=FloatWire()
        self.factor=factor

    def connect(self, wire):
        assert isinstance(wire, FloatWire)
        wire.CHANNELS=self.input_wire.CHANNELS
        wire.FORMAT=self.input_wire.FORMAT
        wire.RATE=self.input_wire.RATE/self.factor
        self.wires.append(wire)

    def connect_input(self, service):
        service.connect(self.input_wire)

    def _process_input(self, data):
        return numpy.max(data.reshape(-1, self.factor),axis=1)

    def _process(self):
        while not self.done:
            try:
                inp=self.receive_input()
            except Exception as ex:
                inp=None
            if inp is not None:
                if not self.stopped:
                    out=self._process_input(inp)
                    self.send_output(out)
            else:
                self.done=True
