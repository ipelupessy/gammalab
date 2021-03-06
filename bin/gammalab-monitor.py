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
from gammalab.acquisition import SoundCard
from gammalab.backend import Monitor
from gammalab.transform import Raw2Float, DownSampleMaxed

def run(input_device_name="", runtime=None, list_input_devices=False):
    if list_input_devices:
      for name, id_ in SoundCard.devices().items():
        print("{0}: {1}".format(name, id_))
      exit(0)

    source=SoundCard(input_device_name=input_device_name)

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
        '--input_device_name',
        dest='input_device_name',
        default="",
        type=str,
        help='select input device by (fuzzy matched) name',
    )
    parser.add_argument(
        '--runtime',
        dest='runtime',
        default=None,
        type=float,
        help='runtime in seconds',
    )
    parser.add_argument(
        '--list_input_devices',
        dest='list_input_devices',
        action="store_true",
        default=False,
        help='list all input devices',
    )    
    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))
