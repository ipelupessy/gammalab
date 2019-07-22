from ..service import ReceivingService
from ..wire import FloatWire

import numpy

try:
    from matplotlib.animation import FuncAnimation
    from matplotlib import pyplot    
    HAS_MATPLOTLIB=True
except:
    HAS_MATPLOTLIB=False

class Monitor(ReceivingService):
    def __init__(self, window=5, vmin=-0.01, vmax=1.1):
        if not HAS_MATPLOTLIB:
            raise Exception("needs matplotlib")
        ReceivingService.__init__(self)
        self.input_wire=FloatWire()
        
        self.window=window
        self.stopped=True
        self.vmin=vmin
        self.vmax=vmax

    def update_plot(self,nframe):
        
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.append(_data)
        
        if data:
            data=numpy.concatenate(data)
        
        if self.stopped:
            return self.plot
        
        while len(data)>0:
          
            n=min(len(data),len(self.plotdata)-self.nplot)
            
            self.plotdata[self.nplot:self.nplot+n]=data[:n]
            data=data[n:]
            self.nplot=(self.nplot+n) % len(self.plotdata)
                            
        self.plot[0].set_ydata(self.plotdata)
        return self.plot
  
    def start(self):
          self.plotdata=numpy.zeros(int(self.input_wire.RATE*self.window), dtype=self.input_wire.FORMAT)
          pyplot.ion()
          f, ax = pyplot.subplots()

          plot=ax.plot(self.plotdata)
          ax.set_ylim(self.vmin,self.vmax)
        
          self.fig=f
          self.ax=ax
          self.plot=plot

          self.stopped=False
          self.nplot=0

          ani = FuncAnimation(self.fig, self.update_plot, interval=50, blit=True)
          f.canvas.draw()

    def stop(self):
        self.stopped=True
      
    def close(self):
        self.stop()
