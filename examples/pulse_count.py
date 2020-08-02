import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed
from gammalab.analysis import PulseDetection
from gammalab.analysis import Count
from gammalab.backend import SoundCardPlay

source=SoundCard()
monitor=Monitor(vmin=-0.01,vmax=0.3)
convert=Raw2Float()
downsample=DownSampleMaxed(factor=16)
detect=PulseDetection(threshold=0.0035)
count=Count()
playback=SoundCardPlay()

source.plugs_into(playback)
source.plugs_into(convert)

convert.plugs_into(detect)
detect.plugs_into(count)

convert.plugs_into(downsample)
downsample.plugs_into(monitor)

main()
