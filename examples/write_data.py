from gammalab import main

from gammalab.acquisition import SoundCard
from gammalab.backend import SaveRaw
from gammalab.transform import Float2Raw

if __name__=="__main__":
    soundcard=SoundCard()
    convert=Float2Raw()
    save=SaveRaw()
    
    soundcard.plugs_into(convert)
    convert.plugs_into(save)
    
    main()
    
