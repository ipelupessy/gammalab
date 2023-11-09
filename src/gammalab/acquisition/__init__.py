from ._soundcard import SoundCard as _SoundCard
from ._sounddevice import SoundDevice
from .generator import Noise
from .file import RawReplay, WavReplay, FileReplay

def SoundCard(sound_api="soundcard", **kwargs):
    if sound_api.lower()=="soundcard":
        return _SoundCard(**kwargs)
    elif sound_api.lower()=="sounddevice":
        return SoundDevice(**kwargs)
    else:
        raise Exception(f"Unknown sound API {sound_api}")
