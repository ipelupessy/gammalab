import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import Noise
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed
from gammalab.analysis import PulseDetection
from gammalab.analysis import Histogram
from gammalab.analysis import Count

source=Noise()
convert=Raw2Float()
detect=PulseDetection(threshold=0.01, window=5000)
count=Count()
histogram=Histogram(nchannels=300,xmin=0,xmax=1.,log=True)

source.plugs_into(convert)

convert.plugs_into(detect)
detect.plugs_into(count)
detect.plugs_into(histogram)

main(100)
