import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import DownSampleMaxed


if __name__=="__main__":
    source=SoundCard()
    monitor=Monitor()
    downsample=DownSampleMaxed(factor=16)
    source.plugs_into(downsample)
    downsample.plugs_into(monitor)
    main()
    
