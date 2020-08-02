from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import SaveRaw

soundcard=SoundCard()
save=SaveRaw()

soundcard.plugs_into(save)

main()
