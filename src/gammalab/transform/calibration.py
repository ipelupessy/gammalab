"""
  Calibration converts raw detector values to energies
"""

from ..service import ReceivingService, SourceService, ThreadService
from ..wire import PulseWire

import numpy

# todo: simplify with inheritance?

class Interpolate(ThreadService, SourceService, ReceivingService):
    def __init__(self, calibration, unit="keV"):
        super(Interpolate, self).__init__()
        self.input_wire=PulseWire()
        self._xp=numpy.array([c[0] for c in calibration])
        self._yp=numpy.array([c[1] for c in calibration])
        try:
            assert(numpy.all(numpy.diff(self._xp) > 0))
        except AssertionError:
            raise Exception("provide ordered calibration dataset")
        self.unit=unit
        
    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data]
        signal=[x[1] for x in data]
        calibrated=numpy.interp(signal, self._xp, self._yp)
        return zip(timestamps, calibrated)

class Scale(ThreadService, SourceService, ReceivingService):
    def __init__(self, scale, unit="keV"):
        super(Scale, self).__init__()
        self.input_wire=PulseWire()
        self.scale=scale
        self.unit=unit
        
    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data]
        scaled=[self.scale*x[1] for x in data]
        return zip(timestamps, scaled)

class SecondOrder(ThreadService, SourceService, ReceivingService):
    def __init__(self, scale, drift=0, unit="keV"):
        super(SecondOrder, self).__init__()
        self.input_wire=PulseWire()
        self.scale=scale
        self.drift=drift
        self.unit=unit
                
    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data]
        scaled=[self.scale*x[1]*(1+self.drift*x[1]) for x in data]
        return zip(timestamps, scaled)
