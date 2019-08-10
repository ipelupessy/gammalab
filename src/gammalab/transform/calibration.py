from ..service import ReceivingService, SourceService, ThreadService
from ..wire import PulseWire

import numpy

class Interpolate(ThreadService, SourceService, ReceivingService):
    def __init__(self, calibration):
        SourceService.__init__(self)
        ReceivingService.__init__(self)
        ThreadService.__init__(self)
        self.input_wire=PulseWire()
        self._xp=numpy.array([c[0] for c in calibration])
        self._yp=numpy.array([c[1] for c in calibration])
        try:
            assert(numpy.all(numpy.diff(self._xp) > 0))
        except AssertionError:
            raise Exception("provide ordered calibartion dataset")
        
    def output_protocol(self, wire):
        assert isinstance(wire, PulseWire)

    def process(self, data):
        timestamps=[x[0] for x in data]
        signal=[x[1] for x in data]
        calibrated=numpy.interp(signal, self._xp, self._yp)
        return zip(timestamps, calibrated)

class Scale(Interpolate):
    def __init__(self, scale):
        calibration=[(0. ,0.),(1., scale)]
        Interpolate.__init__(self, calibration)
