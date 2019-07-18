import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed
from gammalab.transform import PulseDetection

source=SoundCard()
monitor=Monitor()
convert=Raw2Float()
downsample=DownSampleMaxed(factor=16)
detect=PulseDetection(threshold=0.95)


source.plugs_into(convert)
convert.plugs_into(downsample)
convert.plugs_into(detect)
downsample.plugs_into(monitor)


main()
