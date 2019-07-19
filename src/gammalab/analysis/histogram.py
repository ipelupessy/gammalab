from ..service import ReceivingService
from ..wire import PulseWire

import numpy

try:
    from matplotlib.animation import FuncAnimation
    from matplotlib import pyplot    
    HAS_MATPLOTLIB=True
except:
    HAS_MATPLOTLIB=False

class Histogram(ReceivingService):
    def __init__(self, nchannels=100, xmin=0, xmax=1.):
        if not HAS_MATPLOTLIB:
            raise Exception("needs matplotlib")
        ReceivingService.__init__(self)
        self.input_wire=PulseWire()
        
        self.stopped=True
        self.xmin=xmin
        self.xmax=xmax
        self.nchannels=nchannels
        self.all_pulses=[]

    def update_plot(self,nframe):
        
        while True:
            data=self.receive_input(False)
            if data is None:
                break
            if len(data)>0:
                self.all_pulses.extend(data)
                
        if self.stopped:
            return self.plot

        data=[x[1] for x in self.all_pulses]
        
        self.ax.cla()
        self.ax.hist(data, bins=self.nchannels, range=(self.xmin,self.xmax))
        
        
    def start(self):
          pyplot.ion()
          f, ax = pyplot.subplots()

          plot=ax.hist([], bins=self.nchannels, range=(self.xmin,self.xmax))
          #~ ax.set_ylim(0,1.)
          #~ ax.set_xlim(self.xmin,self.xmax)
        
          self.fig=f
          self.ax=ax
          self.plot=plot

          self.stopped=False
          self.nplot=0

          ani = FuncAnimation(self.fig, self.update_plot, interval=200)
          f.canvas.draw()

    def stop(self):
        self.stopped=True
      
    def close(self):
        self.stop()
