import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed, Scale
from gammalab.analysis import PulseDetection
from gammalab.analysis import AggregateHistogram
from gammalab.analysis import Count
from gammalab.backend import SoundCardPlay, PlotHistogram

if __name__=="__main__":

    source=SoundCard()
    monitor=Monitor(vmin=-0.01,vmax=0.1)
    downsample=DownSampleMaxed(factor=8)
    detect=PulseDetection(threshold=0.003)
    count=Count()
    playback=SoundCardPlay()
    calibrate=Scale(scale=5400.)
    histogram=AggregateHistogram(nchannels=5000, vmax=5400)
    plothistogram=PlotHistogram(xmin=0, xmax=2000,log=False)
    
    source.plugs_into(playback)
    source.plugs_into(detect)    
    detect.plugs_into(count)
    detect.plugs_into(calibrate)
    calibrate.plugs_into(histogram)
    histogram.plugs_into(plothistogram)
    
    source.plugs_into(downsample)
    downsample.plugs_into(monitor)
    
    main(100)
    
