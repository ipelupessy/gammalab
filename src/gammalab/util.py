import configparser
import numpy

from datetime import datetime

def calibration_pair(s):
    """
      type for argument parser in order to interpret space seperated list of
      (value,energy) pairs.
    """
    return list(map(float, s.split(",")))

def get_calibration_coeff(data=None, order=2, no_offset=False, 
        return_coeff=False,write_ini=False, read_ini=False):
    """
      calculate calibration coefficients from (raw, energy) pairs
      
      Arguments:
        data: list of (raw_value, energy) pairs of calibration data
        order: order of polynomial fit order =1 or 2 is recommended
        no_offset: boolean indicating whether to force offset to be zero,
        return_coeff: boolean indicating  whether to return raw coefficients or 
                      offset, scale and drift (default).
        write_ini: whether to write out a ini file with calibration data
        read_ini: whether to read ini file with calibration, ignoring any other arguments
        
      Returns:
        tuple of offset, scale and drift: (E=offset+scale*d*(1+d*x))
          or 
        raw coefficients c_i: E=c_0 + c_1*d + ... + c_n*d**n
      
    """
    if read_ini:
        return read_calibration_file()
    
    if data is None or len(data)==0:
        raise Exception("no data, provide data ..")

    if no_offset:
        _offset=0
    else:
        _offset=1
    
    if order>len(data)-_offset:
        print("not enough data points, reducing order")
        order=len(data)-_offset
    
    data=numpy.array(data)
    x=data[:,0]
    y=data[:,1]
    
    a=numpy.zeros((len(x), order+_offset))
    
    for i in range(order+_offset):
        a[:,i]=x**(i+1-_offset)
    
    p=numpy.linalg.pinv(a)
    
    coeff=p.dot(y)
    
    if no_offset:
      coeff=numpy.concatenate([[0],coeff])
    
    offset=coeff[0]
    scale=coeff[1]
    if order>=2:
      drift=coeff[2]/coeff[1]
    
    # ~ print(f"raw coefficents: {coeff}")
    # ~ print(f"the offset is: {offset}")
    # ~ print(f"the scale is: {scale}")
    # ~ print(f"the drift is: {drift}")
    
    if write_ini:
        write_calibration_file(data,order=order,no_offset=no_offset)
    
    if return_coeff:
        return coeff
    else:
        return offset,scale,drift

def read_calibration_file(filename="gammalab.ini"):

    config = configparser.ConfigParser()
    config.read(filename)
    
    label=config["calibration"].get("label","(no label)")
    s=config["calibration"].get("data").split(" ")
    s=[x for x in s if x!=""]
    s=[calibration_pair(x) for x in s]
      
    order=config["calibration"].getint("order", 1)
    no_offset=config["calibration"].getboolean("no_offset", True)
    print(f"[util] calibration read from {filename}, labelled {label}")
    
    return get_calibration_coeff(s, order=order, no_offset=no_offset)

def write_calibration_file(data, filename="gammalab.ini", order=1, no_offset=True, label=None):
    data=" ".join([f"{x[0]},{x[1]}" for x in data])
    if label is None:
        label=f"{datetime.now()}"
    config = configparser.ConfigParser()
    config["calibration"]=dict(data=data, order=order, no_offset=no_offset, label=label)
    with open(filename,'w') as f:
        config.write(f)
    print(f"[util] calibration written to {filename}")
