from ..service import ReceivingService
from ..wire import FloatWire, HistogramWire

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
          self.plotx=numpy.arange(int(self.input_wire.RATE*self.window))/float(self.input_wire.RATE)
          pyplot.ion()
          f, ax = pyplot.subplots()

          plot=ax.plot(self.plotx,self.plotdata)
          ax.set_ylim(self.vmin,self.vmax)
          ax.set_xlabel("time (s)")
          ax.set_ylabel("level")
        
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

class PlotHistogram(ReceivingService):
    def __init__(self, xmin=0, xmax=1., log=True, 
                    error_bars=True, scale=1., outfile="histogram"):
        if not HAS_MATPLOTLIB:
            raise Exception("needs matplotlib")
        ReceivingService.__init__(self)
        self.input_wire=HistogramWire()
        
        self.stopped=True
        self.xmin=xmin
        self.xmax=xmax
        self.log=log
        self.error_bars=error_bars
        self.scale=scale
        self.outfile=outfile
        self.ymax=1.

    def update_plot(self,nframe):
        
        data=None
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data=_data

        if self.stopped or data is None:
            if self.error_bars:
                return self._line,self._top,self._bot
            else:
                return self._line,

        hist=data["hist"]
        bins=data["bins"]

        return self.update_histogram_plot(hist,bins)

    def update_histogram_plot(self, hist, bins):
        y=numpy.zeros(2*len(hist))
        y[::2]=hist
        y[1::2]=hist
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
        nchannels=self.input_wire.nchannels
        vmin=self.input_wire.vmin
        vmax=self.input_wire.vmax
        hist,bins=numpy.histogram([], bins=nchannels, range=(vmin,vmax))
        x=numpy.zeros(2*nchannels)
        y=numpy.zeros(2*nchannels)
        x[::2]=bins[:-1]
        x[1::2]=bins[1:]
        y[::2]=hist
        y[1::2]=hist
        if self.error_bars:
            yerr=y**0.5
            self._top,=self.ax.plot(self.scale*x,numpy.maximum(y+yerr,1),":",c="tab:orange", zorder=0)
            self._bot,=self.ax.plot(self.scale*x,y-yerr,":",c="tab:orange",zorder=5)
        if self.log:
            self._line,=self.ax.semilogy(self.scale*x,y+0.1, lw=2, zorder=10)
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
