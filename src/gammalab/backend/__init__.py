from .raw import SaveRaw
from .wav import SaveWav
from ._soundcard import SoundCardPlay as _SoundCardPlay
from ._sounddevice import SoundDevicePlay
from .plot import Monitor, PlotHistogram, CountPlot, PulsePlot

def SoundCardPlay(sound_api="soundcard", **kwargs):
    if sound_api.lower()=="soundcard":
        return _SoundCardPlay(**kwargs)
    elif sound_api.lower()=="sounddevice":
        return SoundDevicePlay(**kwargs)
    else:
        raise Exception(f"Unknown sound API {sound_api}")
