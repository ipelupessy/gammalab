#!/usr/bin/env python
"""
gammalab-histogram makes a histogram of detected peak heights. 
"""

import argparse

import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard, FileReplay
from gammalab.transform import Raw2Float, Scale
from gammalab.analysis import PulseDetection, FittedPulseDetection
from gammalab.analysis import AggregateHistogram
from gammalab.analysis import Count
from gammalab.backend import PlotHistogram

def run(threshold=0.003, nchannels=500, vmax=2000., scale=5400., 
        runtime=None, outfile=None, log=True, do_plot=True,
        input_device_index=None, inputfile=None, realtime=True,
        fitpulse=False, fit_threshold=0.95):

    if inputfile is not None:
        source=FileReplay(filename=inputfile, realtime=realtime)
    else:
        source=SoundCard(input_device_index=input_device_index)
    convert=Raw2Float()
    if fitpulse:
        detect=FittedPulseDetection(threshold=threshold, fit_threshold=fit_threshold)
    else:
        detect=PulseDetection(threshold=threshold)
    
    count=Count(outfile=None)
    calibrate=Scale(scale=scale)
    histogram=AggregateHistogram(nchannels=int(nchannels*vmax/1000.), vmin=0, vmax=vmax, outfile=outfile)
    
    source.plugs_into(convert)
    
    convert.plugs_into(detect)
    detect.plugs_into(count)
    detect.plugs_into(calibrate)
    calibrate.plugs_into(histogram)

    if do_plot:
        plothistogram=PlotHistogram(xmin=0,xmax=vmax, outfile=outfile, log=log)
        histogram.plugs_into(plothistogram)

    main(runtime)

def new_argument_parser():
    "Parse command line arguments"
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description=__doc__)
    parser.add_argument(
        '--threshold',
        dest='threshold',
        default=0.003,
        type=float,
        help='(noise) threshold for pulse detection',
    )
    parser.add_argument(
        '--nchannels',
        dest='nchannels',
        default=100,
        type=int,
        help='number of channels per MeV (bins) in the histogram',
    )
    parser.add_argument(
        '--vmax',
        dest='vmax',
        default=2000,
        type=float,
        help='maximum energy bin for histogram',
    )
    parser.add_argument(
        '--scale',
        dest='scale',
        default=5400,
        type=float,
        help='signal energy scale (in keV)',
    )
    parser.add_argument(
        '--outfile',
        dest='outfile',
        default=None,
        help='output file root',
    )
    parser.add_argument(
        '--runtime',
        dest='runtime',
        default=None,
        type=float,
        help='runtime in seconds',
    )
    parser.add_argument(
        '--log',
        dest='log',
        action="store_true",
        help='plot logarithmic y-axis',
    )
    parser.add_argument(
        '--no-plot',
        dest='do_plot',
        action="store_false",
        help='hide plot',
    )
    parser.add_argument(
        '--input_device_index',
        dest='input_device_index',
        default=None,
        type=int,
        help='select input device',
    )
    parser.add_argument(
        '--infile',
        dest='inputfile',
        default=None,
        help='(optional) input file',
    ) 
    parser.add_argument(
        '--realtime',
        dest='realtime',
        action="store_true",
        help='file input in realtime',
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
        help='minimum peak to determine amplitude through fitting',
    )

    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))

