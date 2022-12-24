import numpy

def calibration_pair(s):
    """
      type for argument parser in order to interpret space seperated list of
      (value,energy) pairs.
    """
    return list(map(float, s.split(",")))


def get_calibration_coeff(data=None, order=2, no_offset=False, return_coeff=False):
    """
      calculate calibration coefficients from (raw, energy) pairs
      
      Arguments:
        data: list of (raw_value, energy) pairs of calibration data
        order: order of polynomial fit order =1 or 2 is recommended
        no_offset: boolean indicating whether to force offset to be zero,
        return_coeff: boolean indicating  whether to return raw coefficients or 
                      offset, scale and drift (default).
      Returns:
        tuple of offset, scale and drift: (E=offset+scale*d*(1+d*x))
          or 
        raw coefficients c_i: E=c_0 + c_1*d + ... + c_n*d**n
      
    """
    if data is None:
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
    
    print(f"raw coefficents: {coeff}")
    print(f"the offset is: {offset}")
    print(f"the scale is: {scale}")
    print(f"the drift is: {drift}")
    
    if return_coeff:
        return coeff
    else:
        return offset,scale,drift
