import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed
from gammalab.transform import PulseDetection
from gammalab.analysis import Histogram
from gammalab.analysis import Count
from gammalab.backend import Playback

source=SoundCard()
#~ monitor=Monitor(vmin=-0.01,vmax=0.1)
convert=Raw2Float()
#~ downsample=DownSampleMaxed(factor=16)
detect=PulseDetection(threshold=0.0025)
count=Count()
playback=Playback()
histogram=Histogram(nchannels=200,xmin=0,xmax=0.1)

source.plugs_into(playback)
source.plugs_into(convert)

convert.plugs_into(detect)
detect.plugs_into(count)
detect.plugs_into(histogram)

#~ convert.plugs_into(downsample)
#~ downsample.plugs_into(monitor)

main()
