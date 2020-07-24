#!/usr/bin/env python
"""
gammalab-monitor plots raw detector (soundcard) values. 
"""
import argparse

try:
  import matplotlib
  matplotlib.use('TkAgg')
except:
  pass

from gammalab import main
from gammalab.acquisition import PyAudio, SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed

def run(input_device_index=None, runtime=None):
    try:
        source=PyAudio(input_device_index=input_device_index)
    except:
        source=SoundCard(input_device_index=input_device_index)

    monitor=Monitor()
    convert=Raw2Float()
    downsample=DownSampleMaxed(factor=16)
        
    source.plugs_into(convert)
    convert.plugs_into(downsample)
    downsample.plugs_into(monitor)
  
    main(runtime)

def new_argument_parser():
    "Parse command line arguments"
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description=__doc__)
    parser.add_argument(
        '--input_device_index',
        dest='input_device_index',
        default=None,
        type=int,
        help='select input device',
    )
    parser.add_argument(
        '--runtime',
        dest='runtime',
        default=None,
        type=float,
        help='runtime in seconds',
    )
    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))
