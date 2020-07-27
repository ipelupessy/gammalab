from gammalab import main
from gammalab.acquisition import PyAudio, SoundCard
from gammalab.backend import PyAudioPlay, SoundCardPlay

soundcard=SoundCard()
playback=SoundCardPlay()

soundcard.plugs_into(playback)



main()
