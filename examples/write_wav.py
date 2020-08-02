# needs pyaudio

from gammalab import main
from gammalab.acquisition import PyAudio
from gammalab.backend import SaveWav

soundcard=PyAudio(sample_format="int16")
save=SaveWav()

soundcard.plugs_into(save)

main(10)
