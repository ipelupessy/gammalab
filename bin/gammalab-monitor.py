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

from gammalab import main
from gammalab.acquisition import SoundCard, FileReplay
from gammalab.backend import Monitor
from gammalab.backend import SaveRaw
from gammalab.backend import SoundCardPlay
from gammalab.transform import Raw2Float, DownSampleMaxed

def run(input_device_name="", runtime=None, list_input_devices=False, raw_output_file="",
        list_output_devices=False, output_device_name="", inputfile=None):
    if list_input_devices:
      for name, id_ in SoundCard.devices().items():
        print("{0}: {1}".format(name, id_))
      exit(0)
    if list_output_devices:
      for name, id_ in SoundCardPlay.devices().items():
        print("{0}: {1}".format(name, id_))
      exit(0)

    if inputfile is not None:
        source=FileReplay(inputfile)
    else:
        source=SoundCard(input_device_name=input_device_name)

    monitor=Monitor()
    convert=Raw2Float()
    downsample=DownSampleMaxed(factor=8)
        
    source.plugs_into(convert)
    convert.plugs_into(downsample)
    downsample.plugs_into(monitor)

    if raw_output_file!="":
        output_file=raw_output_file+"."+datetime.utcnow().strftime("%Y%m%d%H%M%S")
        save=SaveRaw(output_file)
        source.plugs_into(save)

    if output_device_name!="":
        playback=SoundCardPlay(output_device_name=output_device_name)
        source.plugs_into(playback)


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
    parser.add_argument(
        '--list_output_devices',
        dest='list_output_devices',
        action="store_true",
        default=False,
        help='list output soundcard devices',
    )
    parser.add_argument(
        '--raw_ouput_file',
        dest='raw_output_file',
        default="",
        type=str,
        help='optionally record raw data stream to provided filename (for later analysis) ',
    )
    parser.add_argument(
        '--output_device_name',
        dest='output_device_name',
        default="",
        type=str,
        help='optional output device for playback (fuzzy matched by name)',
    )
    parser.add_argument(
        '--infile',
        dest='inputfile',
        default=None,
        help='Optionally playback from input file',
    ) 
    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))
