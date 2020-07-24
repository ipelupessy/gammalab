from gammalab import main
from gammalab.acquisition import PyAudio
from gammalab.backend import Playback

soundcard=PyAudio()
playback=Playback()

soundcard.plugs_into(playback)



main()
