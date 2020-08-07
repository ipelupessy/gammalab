from ..service import ReceivingService, SourceService, ThreadService
from ..wire import PulseWire

import numpy

class Interpolate(ThreadService, SourceService, ReceivingService):
    input_wire_class=PulseWire
    output_wire_class=PulseWire
    def __init__(self, calibration):
        super(Interpolate, self).__init__()
        self._xp=numpy.array([c[0] for c in calibration])
        self._yp=numpy.array([c[1] for c in calibration])
        try:
            assert(numpy.all(numpy.diff(self._xp) > 0))
        except AssertionError:
            raise Exception("provide ordered calibration dataset")

    def process(self, data):
        timestamps=[x[0] for x in data]
        signal=[x[1] for x in data]
        calibrated=numpy.interp(signal, self._xp, self._yp)
        return zip(timestamps, calibrated)

class Scale(ThreadService, SourceService, ReceivingService):
    input_wire_class=PulseWire
    output_wire_class=PulseWire    
    def __init__(self, scale):
        super(Scale, self).__init__()
        self.scale=scale

    def process(self, data):
        timestamps=[x[0] for x in data]
        scaled=[self.scale*x[1] for x in data]
        return zip(timestamps, scaled)
