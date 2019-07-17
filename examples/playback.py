from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Playback

soundcard=SoundCard()
playback=Playback()

soundcard.plugs_into(playback)



main()
