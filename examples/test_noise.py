from gammalab import main
from gammalab.acquisition import Noise
from gammalab.backend import SaveRaw

source=Noise()
save=SaveRaw()

source.plugs_into(save)

main()
