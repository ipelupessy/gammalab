#!/usr/bin/env python
"""
gammalab-histogram makes a histogram of detected peak heights. 
"""
import os
import argparse

try:
  import matplotlib
  matplotlib.use('TkAgg')
except:
  pass

from gammalapp import run

def new_argument_parser():
    "Parse command line arguments"
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description=__doc__, epilog="Note: if a gammalab.ini file is present and --raw not given, the calibration data in the file is used to determine offset,scale and drift")

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
        '--input-file',
        dest='inputfile',
        default=None,
        help='(optional) analyze from input file',
    )
    parser.add_argument(
        '--plot',
        dest='do_plot',
        action="store_true",
        help='show histogram plot',
    )
    parser.add_argument(
        '--plot-count',
        dest='plot_count',
        action="store_true",
        help='show plot of counts',
    )
    parser.add_argument(
        '--plot-pulses',
        dest='plot_pulses',
        action="store_true",
        help='Plot sampling of pulse shapes',
    )    
    parser.add_argument(
        '--log',
        dest='log',
        action="store_true",
        help='plot histogram with logarithmic y-axis',
    )
    parser.add_argument(
        '--raw',
        dest='raw_values',
        action="store_true",
        help='histogram of normalized raw detector values (no calibration)',
    )
    parser.add_argument(
        '--nchannels',
        dest='nchannels',
        default=200,
        type=int,
        help='number of channels (bins) in the histogram',
    )
    parser.add_argument(
        '--max_energy',
        dest='vmax',
        default=2000,
        type=float,
        help='maximum energy bin for histogram (keV, ignored for --raw)',
    )
    parser.add_argument(
        '--baseline',
        dest='baseline',
        default=0.,
        type=float,
        help='signal baseline (raw value)',
    )
    parser.add_argument(
        '--negative_peaks',
        dest='negative_peaks',
        action="store_true",
        default=False,
        help='inverted (negative peak) signal',
    )
    parser.add_argument(
        '--amplitude',
        dest='amplitude',
        default=1.,
        type=float,
        help='max signal amplitude for normalization (raw value)',
    )
    parser.add_argument(
        '--threshold',
        dest='threshold',
        default=0.003,
        type=float,
        help='(noise) threshold for pulse detection (normalized raw value)',
    )              
    parser.add_argument(
        '--offset',
        dest='offset',
        default=0.,
        type=float,
        help='signal energy offset (in keV)',
    )
    parser.add_argument(
        '--scale',
        dest='scale',
        default=5400,
        type=float,
        help='signal energy scale (in keV, ignored for --raw)',
    )
    parser.add_argument(
        '--drift',
        dest='drift',
        default=0,
        type=float,
        help='second order correction parameter (fractional deviation at raw value 1)',
    )
    parser.add_argument(
        '--fitpulse',
        dest='fitpulse',
        action="store_true",
        help='use pulse fitting for amplitude?',
    )       
    parser.add_argument(
        '--fit-threshold',
        dest='fit_threshold',
        default=0.95,
        type=float,
        help='minimum peak to determine amplitude through fitting (normalized raw value)',
    )    
    parser.add_argument(
        '--outfile',
        dest='outfile',
        default=None,
        help='output file root',
    )    
    parser.add_argument(
        '--histogram-mode',
        dest='histogram_mode',
        default="normal",
        type=str,
        help='mode for histogram binning (normal, proportional, semiprop, quadratic)',
    )
    parser.add_argument(
        '--time-normalized',
        dest='time_normalized',
        action="store_true",
        help='plot time normalized histogram',
    )
    parser.add_argument(
        '--plot-excess',
        dest='plot_excess',
        action="store_true",
        help='Plot excess counts in histogram (needs --background)',
    )        
    parser.add_argument(
        '--background',
        dest='background',
        default="",
        type=str,
        help='optional filename for background spectrum in histogram plot (recommended to add --time_normalized)',
    )     
    parser.add_argument(
        '--realtime',
        dest='realtime',
        action="store_true",
        help='file input in realtime',
    )       
    parser.add_argument(
        '--sound-api',
        dest='sound_api',
        default="SoundCard",
        help='Sound Card API to use [soundcard, sounddevice]',
    )    
    parser.add_argument(
        '--dose',
        dest='dose',
        action="store_true",
        help='show dose estimate',
    )       
    parser.add_argument(
        '--detector-mass',
        dest='detector_mass',
        default=0.01,
        type=float,
        help='detector mass (only needed for dose estimate) [0.01] ',
    )
    return parser

if __name__=="__main__":
    args = new_argument_parser().parse_args()
    run(**vars(args))

