#!/usr/bin/env python
"""
gammalab-histogram makes a histogram of detected peak heights. 
"""

import argparse

import matplotlib
matplotlib.use('TkAgg')

from gammalab import main
from gammalab.acquisition import SoundCard
from gammalab.transform import Raw2Float
from gammalab.analysis import PulseDetection
from gammalab.analysis import AggregateHistogram
from gammalab.analysis import Count
from gammalab.backend import PlotHistogram

def run(threshold=0.003, nchannels=500, xmax=2000., scale=5400., runtime=None, outfile=None, log=True, do_plot=True):

    source=SoundCard()
    convert=Raw2Float()
    detect=PulseDetection(threshold=threshold)
    count=Count(outfile=None)
    histogram=AggregateHistogram(nchannels=nchannels, outfile=outfile)
    
    source.plugs_into(convert)
    
    convert.plugs_into(detect)
    detect.plugs_into(count)
    detect.plugs_into(histogram)
    
    if do_plot:
      plothistogram=PlotHistogram(xmin=0,xmax=xmax, scale=scale, outfile=outfile, log=log)
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
        default=500,
        type=int,
        help='number of channels (bins) in the histogram',
    )
    parser.add_argument(
        '--xmax',
        dest='xmax',
        default=2000,
        type=float,
        help='Maximum energy',
    )
    parser.add_argument(
        '--scale',
        dest='scale',
        default=5400,
        type=float,
        help='Energy scale',
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
    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))

