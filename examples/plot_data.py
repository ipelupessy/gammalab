import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import PyAudio
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed

source=PyAudio()
monitor=Monitor()
convert=Raw2Float()
downsample=DownSampleMaxed(factor=16)


source.plugs_into(convert)
convert.plugs_into(downsample)
downsample.plugs_into(monitor)


main()
