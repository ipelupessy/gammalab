from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import SoundCardPlay

if __name__=="__main__":
    soundcard=SoundCard()
    playback=SoundCardPlay()
    
    soundcard.plugs_into(playback)
    
    main()
    
