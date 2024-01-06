#!/usr/bin/env python
"""
gammalab-monitor plots raw detector (soundcard) values. 
"""
import argparse
from datetime import datetime

try:
  import matplotlib
  matplotlib.use('TkAgg')
except:
  pass

from gammalapp import run

def new_argument_parser():
    "Parse command line arguments"
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description=__doc__)

    parser.add_argument(
        '--runtime',
        dest='runtime',
        default=None,
        type=float,
        help='runtime in seconds',
    )
    parser.add_argument(
        '--input-device',
        dest='input_device_name',
        default="",
        type=str,
        help='select input device by (fuzzy matched) name',
    )
    parser.add_argument(
        '--output-device',
        dest='output_device_name',
        default="",
        type=str,
        help='optional output device for playback (fuzzy matched by name)',
    )
    parser.add_argument(
        '--list-devices',
        dest='list_devices',
        action="store_true",
        default=False,
        help='list available input and output devices',
    )
    parser.add_argument(
        '--output-file',
        dest='raw_output_file',
        default="",
        type=str,
        help='optionally record raw data stream to provided filename (for later analysis) ',
    )
    parser.add_argument(
        '--input-file',
        dest='inputfile',
        default=None,
        help='Optionally playback from input file',
    ) 
    parser.add_argument(
        '--sound-api',
        dest='sound_api',
        default="SoundCard",
        help='Sound Card API to use [soundcard, sounddevice]',
    )    
    return parser

if __name__=="__main__":
    args = new_argument_parser().parse_args()
    args=vars(args)
    args["monitor"]=True
    args["detect"]=False
    run(**args)
