#!/usr/bin/env python
"""
gammalab-histogram makes a histogram of detected peak heights. 
"""
import os
import argparse

from datetime import datetime

try:
  import matplotlib
  matplotlib.use('TkAgg')
except:
  pass

from gammalab import main
from gammalab.util import read_calibration_file
from gammalab.acquisition import SoundCard, FileReplay
from gammalab.transform import DownSampleMaxed
from gammalab.transform import Normalize, SecondOrder
from gammalab.analysis import PulseDetection, FittedPulseDetection
from gammalab.analysis import AggregateHistogram
from gammalab.analysis import Count, DoseCount
from gammalab.backend import PlotHistogram, CountPlot, PulsePlot
from gammalab.backend import SaveRaw
from gammalab.backend import SoundCardPlay
from gammalab.backend import Monitor


def run(threshold=0.003, nchannels=500, vmax=2000., offset=0, scale=5000., 
        drift=0., runtime=None, outfile=None, log=True, do_plot=False,
        input_device_name="", inputfile=None, realtime=True,
        fitpulse=False, fit_threshold=0.95, raw_values=False,
        baseline=0., negative_peaks=False, amplitude=1., plot_count=False,
        histogram_mode="normal", background="", plot_pulses=False,
        time_normalized=False, plot_excess=False,sound_api="soundcard", dose=False, 
        detector_mass=None, list_devices=False, raw_output_file="", output_device_name="", 
        monitor=False, detect=True):

    if list_devices:
        print("Input devices:")
        for name, id_ in SoundCard(sound_api=sound_api).devices().items():
            print(f"  {name}: {id_}")
        print("Output devices:")
        for name, id_ in SoundCardPlay(sound_api=sound_api).devices().items():
            print(f"  {name}: {id_}")
        exit(0)

    detect=detect or do_plot or plot_pulses or plot_count or fitpulse or (outfile is not None) or dose or raw_values

    if dose and raw_values:
        raise Exception("Dose estimate cannot be done on raw values (remove --dose or --raw")

    if raw_values:
        scale=1.
        vmax=1.
    else:
        if os.path.isfile("gammalab.ini"):
            offset,scale,drift=read_calibration_file("gammalab.ini")
        
        print(f"using offset={offset:5.2f}, scale={scale:5.2f}, drift={drift:5.2f}")

    if inputfile is not None:
        source=FileReplay(filename=inputfile, realtime=realtime)
    else:
        source=SoundCard(sound_api=sound_api,input_device_name=input_device_name)

    if monitor:
        monitor_=Monitor()
        downsample=DownSampleMaxed(factor=8)
            
        source.plugs_into(downsample)
        downsample.plugs_into(monitor_)

    if detect:

        normalize=Normalize(baseline=baseline, scale=-amplitude if negative_peaks else amplitude)
    
        pulse_file=outfile+".pulses" if outfile is not None else None
        if fitpulse:
            detect=FittedPulseDetection(threshold=threshold, fit_threshold=fit_threshold,
                                        outfile=pulse_file,emit_pulse_shapes=True)
        else:
            detect=PulseDetection(threshold=threshold, 
                                  outfile=pulse_file,emit_pulse_shapes=True)
        
        histogram=AggregateHistogram(nchannels=int(nchannels),
                                     vmin=threshold*scale, 
                                     vmax=vmax, 
                                     outfile=outfile+".histogram" if outfile is not None else None,
                                     histogram_mode=histogram_mode)
        
        source.plugs_into(normalize)
        normalize.plugs_into(detect)
            
        if raw_values:
            detect.plugs_into(histogram)
            detect_=detect
        else:
            calibrate=SecondOrder(offset=offset, scale=scale, drift=drift)
            detect.plugs_into(calibrate)
            calibrate.plugs_into(histogram)
            detect_=calibrate
    
        if dose:
            count=DoseCount(outfile=outfile+".dosecounts" if outfile is not None else None, runtime=runtime, detector_mass=detector_mass)
            detect_.plugs_into(count)
        else:
            count=Count(outfile=outfile+".counts" if outfile is not None else None, runtime=runtime)
            detect_.plugs_into(count)

    if plot_pulses:
        pulseplot=PulsePlot(nplot=5,
                            interval=1000)
        detect.plugs_into(pulseplot)

    if plot_count:
        countplot=CountPlot(outfile=outfile+".count" if outfile is not None else None)
        count.plugs_into(countplot)

    if do_plot:
        plothistogram=PlotHistogram(xmin=0, 
                                    xmax=vmax, 
                                    outfile=outfile,
                                    log=log,
                                    background=background,
                                    time_normalized=time_normalized,
                                    plot_excess=plot_excess)
        histogram.plugs_into(plothistogram)

    if raw_output_file!="":
        output_file=raw_output_file+"."+datetime.utcnow().strftime("%Y%m%d%H%M%S")
        save=SaveRaw(output_file)
        source.plugs_into(save)

    if output_device_name!="":
        playback=SoundCardPlay(sound_api=sound_api,output_device_name=output_device_name)
        source.plugs_into(playback)

    main(runtime)

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
        '--output-device',
        dest='output_device_name',
        default="",
        type=str,
        help='optional output device for playback (fuzzy matched by name)',
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
        '--output-file',
        dest='outfile',
        default=None,
        help='output file root for analysis results (histogram etc)',
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
        default=None,
        type=float,
        help='detector mass (only needed for dose estimate) [0.01] ',
    )
    parser.add_argument(
        '--raw-output-file',
        dest='raw_output_file',
        default="",
        type=str,
        help='optionally record raw data stream to provided filename (for later analysis) ',
    )
    parser.add_argument(
        '--list-devices',
        dest='list_devices',
        action="store_true",
        default=False,
        help='list available input and output devices',
    )
    parser.add_argument(
        '--monitor',
        dest='monitor',
        action="store_true",
        default=False,
        help='monitor raw detector output',
    )
    return parser

if __name__=="__main__":
    args = new_argument_parser().parse_args()
    run(**vars(args))

