from ..service import ReceivingService
from ..wire import PulseWire

import time
import numpy
import pickle

try:
    from matplotlib.animation import FuncAnimation
    from matplotlib import pyplot    
    HAS_MATPLOTLIB=True
except:
    HAS_MATPLOTLIB=False

class Histogram(ReceivingService):
    def __init__(self, nchannels=100, xmin=0, xmax=1., log=True, 
                    error_bars=True, scale=1., outfile="histogram"):
        if not HAS_MATPLOTLIB:
            raise Exception("needs matplotlib")
        ReceivingService.__init__(self)
        self.input_wire=PulseWire()
        
        self.stopped=True
        self.xmin=xmin
        self.xmax=xmax
        self.nchannels=nchannels
        self.hist, self.bins=numpy.histogram([0], bins=self.nchannels, range=(0.,1.))
        self.log=log
        self.error_bars=error_bars
        self.scale=scale
        self.outfile=outfile
        self.ymax=1.

    def update_plot(self,nframe):
        
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.extend(_data)
                
        if self.stopped or len(data)==0:
            if self.error_bars:
                return self._line,self._top,self._bot
            else:
                return self._line,

        data=[x[1] for x in data]
        
        hist,bins=numpy.histogram(data, bins=self.nchannels, range=(0.,1.))
        
        self.hist=self.hist+hist
        
        return self.update_histogram_plot()

    def update_histogram_plot(self):
        y=numpy.zeros(2*self.nchannels)
        y[::2]=self.hist
        y[1::2]=self.hist
        yerr=y**0.5
        self._line.set_ydata(y)
        self._update_ylim(y.max())
        if self.error_bars:
            self._top.set_ydata(numpy.maximum(y+yerr,1))
            self._bot.set_ydata(y-yerr)
            return self._line,self._top,self._bot
        else:
            return self._line,

    def _update_ylim(self,ymax):
        if self.log:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=10*_ymax
                self.ax.set_ylim(1,2*self.ymax)
        else:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=1.5*ymax
                self.ax.set_ylim(0,1.3*self.ymax)      

    def _histogram_plot(self):
        self.ax.cla()
        x=numpy.zeros(2*self.nchannels)
        y=numpy.zeros(2*self.nchannels)
        x[::2]=self.bins[:-1]
        x[1::2]=self.bins[1:]
        y[::2]=self.hist
        y[1::2]=self.hist
        if self.error_bars:
            yerr=y**0.5
            self._top,=self.ax.plot(self.scale*x,numpy.maximum(y+yerr,1),":",c="tab:orange", zorder=0)
            self._bot,=self.ax.plot(self.scale*x,y-yerr,":",c="tab:orange",zorder=5)
        if self.log:
            self._line,=self.ax.semilogy(self.scale*x,y, lw=2, zorder=10)
        else:
            self._line,=self.ax.plot(self.scale*x,y,lw=2, zorder=10)

        self.ax.set_ylabel("counts")
        self.ax.set_xlabel("level" if self.scale==1. else "energy (keV)")
        self.ax.set_xlim(self.xmin,self.xmax)
        self._update_ylim(max(y.max(),50))
      
    def start(self):
        pyplot.ion()
        self.fig, self.ax = pyplot.subplots()
      
        self._histogram_plot()
      
        self.stopped=False

        ani = FuncAnimation(self.fig, self.update_plot, interval=250, blit=True)
        self.fig.canvas.draw()

    def stop(self):
        self.stopped=True
      
    def close(self):
        self.stop()
        if self.outfile is not None:
            time.sleep(0.3)
            self.fig.savefig(self.outfile+'.png')
            f=open(self.outfile+'.pkl',"wb")
            pickle.dump((self.hist, self.bins),f)
            f.close()        
  
