from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.analysis import PulseDetection
from gammalab.analysis import Count
from gammalab.backend import PulsePlot

if __name__=="__main__":
    source=SoundCard(input_device_name="PCM2900")
    detect=PulseDetection(threshold=0.004, emit_pulse_shapes=True)
    count=Count()
    pulseplot=PulsePlot(nplot=5)
    
    source.plugs_into(detect)
    detect.plugs_into(count)
    detect.plugs_into(pulseplot)
    
    main()
    
