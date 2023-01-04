import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import WavReplay
from gammalab.backend import Monitor
from gammalab.transform import DownSampleMaxed, Int162Float


if __name__=="__main__":
    source=WavReplay("test.wav")
    convert=Int162Float()
    monitor=Monitor()
    downsample=DownSampleMaxed(factor=16)
    source.plugs_into(convert)
    convert.plugs_into(downsample)
    downsample.plugs_into(monitor)
    main()
    
