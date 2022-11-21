#!/usr/bin/env python
"""
gammalab-calibration-cal determines calibration coeff for a polynomial calibration curve. 
"""


import argparse
import numpy

def calibration_pair(s):
    return list(map(float, s.split(",")))

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
        help='order of calibration polynomial fit',
    )
  
    return parser.parse_args()

def run(data=None, order=2):
    if data is None:
        raise Exception("no data, provide --data ..")
    
    if order>len(data):
        order=len(data)
    
    data=numpy.array(data)
    x=data[:,0]
    y=data[:,1]
    
    a=numpy.zeros((len(x), order))
    
    for i in range(order):
        a[:,i]=x**(i+1)
    
    p=numpy.linalg.pinv(a)
    
    coeff=p.dot(y)
    
    print(f"raw coefficents: {coeff}")
    print(f"the scale is: {coeff[0]}")
    if order>=2:
        print(f"the drift is: {coeff[1]/coeff[0]}")
    
    

if __name__=="__main__":
    args=new_argument_parser()
    run(**vars(args))
