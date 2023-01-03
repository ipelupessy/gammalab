"""
  Calibration converts raw detector values to energies
"""

from ..service import ReceivingService, SourceService, ThreadService
from ..wire import PulseWire

import numpy

# todo: simplify with inheritance?

class Interpolate(ThreadService, SourceService, ReceivingService):
    input_wire_class=PulseWire
    output_wire_class=PulseWire

    def __init__(self, calibration, unit="keV"):
        super().__init__()
        self._xp=numpy.array([c[0] for c in calibration])
        self._yp=numpy.array([c[1] for c in calibration])
        try:
            assert(numpy.all(numpy.diff(self._xp) > 0))
        except AssertionError:
            raise Exception("provide ordered calibration dataset")
        self.unit=unit
        
    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data["pulses"]]
        signal=[x[1] for x in data["pulses"]]
        calibrated=numpy.interp(signal, self._xp, self._yp)
        data["pulses"]=zip(timestamps, calibrated)
        return data

class Scale(ThreadService, SourceService, ReceivingService):
    input_wire_class=PulseWire
    output_wire_class=PulseWire    

    def __init__(self, scale, unit="keV"):
        super().__init__()
        self.scale=scale
        self.unit=unit
        
    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data["pulses"]]
        scaled=[self.scale*x[1] for x in data["pulses"]]
        data["pulses"]=zip(timestamps, scaled)
        return data

class SecondOrder(ThreadService, SourceService, ReceivingService):
    input_wire_class=PulseWire
    output_wire_class=PulseWire    

    def __init__(self, scale, offset=0., drift=00, unit="keV"):
        super().__init__()
        self.input_wire=PulseWire()
        self.scale=scale
        self.drift=drift
        self.offset=offset
        self.unit=unit
                
    def output_protocol(self, wire):
        super().output_protocol(wire)
        wire.unit=self.unit

    def process(self, data):
        timestamps=[x[0] for x in data["pulses"]]
        scaled=[self.offset+self.scale*x[1]*(1+self.drift*x[1]) for x in data["pulses"]]
        data["pulses"]=zip(timestamps, scaled)
        return data
