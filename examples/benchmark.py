from gammalab import main
from gammalab.acquisition import Noise
from gammalab.backend import SaveRaw
from gammalab.transform.simple import Identity

def test1(n=10):
    source=Noise()
    c=[]
    for i in range(n):
        c.append(Identity())
    save=SaveRaw()
    
    source.plugs_into(c[0])
    for i in range(n-1):
      c[i].plugs_into(c[i+1])
    c[-1].plugs_into(save)
    
    main()
    
def test2(n=1):
    source=Noise(frames_per_buffer=128)
    c=[]
    for i in range(n):
        c.append(Identity())
    save=SaveRaw()
    
    source.plugs_into(c[0])
    for i in range(n-1):
      c[i].plugs_into(c[i+1])
    c[-1].plugs_into(save)
    
    main()

if __name__=="__main__":
    test2()
