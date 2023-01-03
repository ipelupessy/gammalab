import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.analysis import PulseDetection
from gammalab.analysis import Count
from gammalab.backend import CountPlot

if __name__=="__main__":
    source=SoundCard(input_device_name="PCM2900")
    detect=PulseDetection(threshold=0.003)
    count=Count()
    countplot=CountPlot()
    
    source.plugs_into(detect)
    detect.plugs_into(count)
    count.plugs_into(countplot)
    
    main()
    
