#!/usr/bin/env python
"""
gammalab-calibration-cal determines calibration coeff for a polynomial calibration curve. 
"""


import argparse
import numpy
from gammalab.util import get_calibration_coeff, calibration_pair

def new_argument_parser():

    parser = argparse.ArgumentParser(description='Determine scale and drift parameters from calibration data')
    parser.add_argument(
        dest='data', 
        default=None, 
        nargs="*", 
        type=calibration_pair,
        help='calibration data: a list of space sperated <raw value>,<energy> pairs, e.g.: 0.1,100 0.5,500.'
    )

    parser.add_argument(
        '--order',
        dest='order',
        default=2,
        type=int,
        help='order of calibration polynomial fit (1 or 2)',
    )
    parser.add_argument(
        '--no_offset',
        dest='no_offset',
        action="store_true",
        default=False,
        help='force offset to be 0.',
    )
    parser.add_argument(
        '--write_ini',
        dest='write_ini',
        action="store_true",
        default=False,
        help='write calibration data to a file (gammalab.ini)',
    )
  
    return parser

if __name__=="__main__":
    args=new_argument_parser().parse_args()
    offset,scale,drift=get_calibration_coeff(**vars(args))
    print("[gammalab-calibration-calc] Calibration parameters:")
    print(f" the offset is: {offset}")
    print(f" the scale is: {scale}")
    print(f" the drift is: {drift}")
