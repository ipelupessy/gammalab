import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import DownSampleMaxed
from gammalab.analysis import PulseDetection
from gammalab.analysis import Count
from gammalab.backend import SoundCardPlay

if __name__=="__main__":
    source=SoundCard()
    monitor=Monitor(vmin=-0.01,vmax=0.3)
    downsample=DownSampleMaxed(factor=16)
    detect=PulseDetection(threshold=0.0035)
    count=Count()
    playback=SoundCardPlay()
    
    source.plugs_into(playback)
    source.plugs_into(detect)
    
    detect.plugs_into(count)
    source.plugs_into(downsample)
    downsample.plugs_into(monitor)
    
    main()
    
