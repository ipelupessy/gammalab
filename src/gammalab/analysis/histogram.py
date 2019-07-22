from ..service import ReceivingService
from ..wire import PulseWire

import numpy
import pickle

try:
    from matplotlib.animation import FuncAnimation
    from matplotlib import pyplot    
    HAS_MATPLOTLIB=True
except:
    HAS_MATPLOTLIB=False

class Histogram(ReceivingService):
    def __init__(self, nchannels=100, xmin=0, xmax=1., log=True, error_bars=True):
        if not HAS_MATPLOTLIB:
            raise Exception("needs matplotlib")
        ReceivingService.__init__(self)
        self.input_wire=PulseWire()
        
        self.stopped=True
        self.xmin=xmin
        self.xmax=xmax
        self.nchannels=nchannels
        self.hist=None
        self.bins=None
        self.log=log
        self.error_bars=error_bars

    def update_plot(self,nframe):
        
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.extend(_data)
                
        if self.stopped or len(data)==0:
            return

        try:
          data=[x[1] for x in data]
        except:
          print data
          raise
        
        hist,bins=numpy.histogram(data, bins=self.nchannels, range=(self.xmin,self.xmax))
        
        self.hist=self.hist+hist
        
        self.ax.cla()
        x=numpy.zeros(2*self.nchannels)
        y=numpy.zeros(2*self.nchannels)
        x[::2]=self.bins[:-1]
        x[1::2]=self.bins[1:]
        y[::2]=self.hist
        y[1::2]=self.hist
        if self.log:
            self.ax.semilogy(x,y)
        else:
            self.ax.plot(x,y)
        if self.error_bars:
            self.ax.errorbar(
            (self.bins[:-1]+self.bins[1:])/2,
            self.hist,
            yerr = self.hist**0.5+1,
            marker = '.',
            fmt="none",
            drawstyle = 'steps-mid'
            )
        
        
        #~ self.ax.hist(data, bins=self.nchannels, range=(self.xmin,self.xmax), log=self.log)
        self.ax.set_ylabel("counts")
        self.ax.set_xlabel("level/energy")

        
    def start(self):
          pyplot.ion()
          f, ax = pyplot.subplots()

          hist,bins=numpy.histogram([0.], bins=self.nchannels, range=(self.xmin,self.xmax))
          
          self.hist=hist
          self.bins=bins
        
          self.fig=f
          self.ax=ax
          x=numpy.zeros(2*self.nchannels)
          y=numpy.zeros(2*self.nchannels)
          x[::2]=self.bins[:-1]
          x[1::2]=self.bins[1:]
          y[::2]=self.hist
          y[1::2]=self.hist

          if self.log:
              self.ax.semilogy(x,y+1)
          else:
              self.ax.plot(x,y)
          self.ax.set_ylabel("counts")
          self.ax.set_xlabel("level/energy")
          
          self.stopped=False
          self.nplot=0

          ani = FuncAnimation(self.fig, self.update_plot, interval=200)
          f.canvas.draw()

    def stop(self):
        self.stopped=True
      
    def close(self):
        self.fig.savefig("histogram.png")
        f=open("histogram.pkl","w")
        pickle.dump((self.hist, self.bins),f)
        f.close()        
        self.stop()
