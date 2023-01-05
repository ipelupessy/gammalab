#!/usr/bin/env python
"""
gammalab-histogram makes a histogram of detected peak heights. 
"""

import argparse

try:
  import matplotlib
  matplotlib.use('TkAgg')
except:
  pass

from gammalab import main
from gammalab.acquisition import SoundCard, FileReplay
from gammalab.transform import Normalize, SecondOrder
from gammalab.analysis import PulseDetection, FittedPulseDetection
from gammalab.analysis import AggregateHistogram
from gammalab.analysis import Count
from gammalab.backend import PlotHistogram, CountPlot, PulsePlot

def run(threshold=0.003, nchannels=500, vmax=2000., offset=0, scale=5000., 
        drift=0., runtime=None, outfile=None, log=True, do_plot=True,
        input_device_name="", inputfile=None, realtime=True,
        fitpulse=False, fit_threshold=0.95, raw_values=False,
        baseline=0., negative_peaks=False, amplitude=1., plot_count=False,
        histogram_mode="normal", background="", plot_pulses=False,
        time_normalized=False):

    if raw_values:
        scale=1.
        vmax=1.

    if inputfile is not None:
        source=FileReplay(filename=inputfile, realtime=realtime)
    else:
        source=SoundCard(input_device_name=input_device_name)

    normalize=Normalize(baseline=baseline, scale=-amplitude if negative_peaks else amplitude)

    pulse_file=outfile+".pulses" if outfile is not None else None
    if fitpulse:
        detect=FittedPulseDetection(threshold=threshold, fit_threshold=fit_threshold,
                                    outfile=pulse_file,emit_pulse_shapes=True)
    else:
        detect=PulseDetection(threshold=threshold, 
                              outfile=pulse_file,emit_pulse_shapes=True)
    
    count=Count(outfile=outfile+".counts" if outfile is not None else None)
    histogram=AggregateHistogram(nchannels=int(nchannels),
                                 vmin=threshold*scale, 
                                 vmax=vmax, 
                                 outfile=outfile+".histogram" if outfile is not None else None,
                                 histogram_mode=histogram_mode)
    
    source.plugs_into(normalize)
    normalize.plugs_into(detect)
    detect.plugs_into(count)
    
    if plot_count:
        countplot=CountPlot(outfile=outfile+".count" if outfile is not None else None)
        count.plugs_into(countplot)

    if plot_pulses:
        pulseplot=PulsePlot(nplot=5,
                            interval=1000)
        detect.plugs_into(pulseplot)

    if raw_values:
        detect.plugs_into(histogram)
    else:
        calibrate=SecondOrder(offset=offset, scale=scale, drift=drift)
        detect.plugs_into(calibrate)
        calibrate.plugs_into(histogram)

    if do_plot:
        plothistogram=PlotHistogram(xmin=0, 
                                    xmax=vmax, 
                                    outfile=outfile,
                                    log=log,
                                    background=background,
                                    time_normalized=time_normalized)
        histogram.plugs_into(plothistogram)

    main(runtime)

def new_argument_parser():
    "Parse command line arguments"
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description=__doc__)

    parser.add_argument(
        '--raw',
        dest='raw_values',
        action="store_true",
        help='histogram of normalized raw detector values (no calibration)',
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
        '--runtime',
        dest='runtime',
        default=None,
        type=float,
        help='runtime in seconds',
    )
    parser.add_argument(
        '--do-plot',
        dest='do_plot',
        action="store_true",
        help='show histogram plot',
    )
    parser.add_argument(
        '--log',
        dest='log',
        action="store_true",
        help='plot histogram with logarithmic y-axis',
    )    
    parser.add_argument(
        '--histogram_mode',
        dest='histogram_mode',
        default="normal",
        type=str,
        help='mode for histogram binning (normal, proportional, semiprop, quadratic)',
    )
    parser.add_argument(
        '--time_normalized',
        dest='time_normalized',
        action="store_true",
        help='plot time normalized histogram',
    )
    parser.add_argument(
        '--background',
        dest='background',
        default="",
        type=str,
        help='optional filename for background spectrum in histogram plot (recommended to add --time_normalized)',
    )    
    parser.add_argument(
        '--plot_count',
        dest='plot_count',
        action="store_true",
        help='show plot of counts',
    )
    parser.add_argument(
        '--plot_pulses',
        dest='plot_pulses',
        action="store_true",
        help='Plot sampling of pulse shapes',
    )    
    parser.add_argument(
        '--input_device_name',
        dest='input_device_name',
        default="",
        type=str,
        help='select input device by (fuzzy matched) name',
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
    
    return parser.parse_args()

if __name__=="__main__":
    args = new_argument_parser()
    run(**vars(args))

