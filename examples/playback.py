from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import SoundCardPlay

soundcard=SoundCard()
playback=SoundCardPlay()

soundcard.plugs_into(playback)



main()
