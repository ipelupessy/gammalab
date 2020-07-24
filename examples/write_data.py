from gammalab import main
from gammalab.acquisition import PyAudio
from gammalab.backend import SaveRaw

soundcard=PyAudio()
save=SaveRaw()

soundcard.plugs_into(save)

main()
