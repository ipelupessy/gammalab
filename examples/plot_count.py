import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.transform import Raw2Float
from gammalab.analysis import PulseDetection
from gammalab.analysis import Count
from gammalab.backend import CountPlot


source=SoundCard(input_device_name="PCM2900")
convert=Raw2Float()
detect=PulseDetection(threshold=0.003)
count=Count()
countplot=CountPlot()

source.plugs_into(convert)
convert.plugs_into(detect)
detect.plugs_into(count)
count.plugs_into(countplot)

main()
